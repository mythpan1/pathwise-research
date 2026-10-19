#!/usr/bin/env python3
"""Advance an explicitly authorized PR using coordinator-owned review evidence."""
import argparse
import fcntl
import json
from pathlib import Path
import subprocess

REPOSITORY = 'mythpan1/pathwise-research'
WORKFLOW = '.github/workflows/validation.yml'
STATE_DIR = Path.home() / '.codex' / 'pathwise-review'


def decision(stage, reason, draft=True):
    return {'stage': stage, 'reason': reason, 'draft': draft}


def evaluate(task, snapshot):
    """Pure, fail-closed state transition; no PR text is an authorization."""
    if snapshot.get('merged'):
        return decision('done', 'already merged', False)
    if snapshot.get('state') != 'open':
        return decision('stop', 'PR is closed')
    auth = task.get('authorization', {})
    if (task.get('repository') != REPOSITORY or auth.get('auto_advance') is not True
            or not auth.get('source') or not isinstance(auth.get('paths'), list)):
        return decision('escalate', 'missing explicit scoped authorization')
    if snapshot.get('head_repository') != REPOSITORY or snapshot.get('base_ref') != 'main':
        return decision('escalate', 'unexpected repository or base branch')
    files = snapshot.get('files')
    if not isinstance(files, list) or not files or not set(files) <= set(auth['paths']):
        return decision('escalate', 'changed paths exceed authorized scope')
    forbidden = ('local/', 'private/', 'sources/originals/', '.acp/', '.dsh/', 'logs/')
    if any(p.startswith(forbidden) or (p.startswith('data/') and p != 'data/README.md')
           for p in files):
        return decision('escalate', 'local or original data is outside automatic scope')
    if task.get('base_sha') != snapshot.get('base_sha'):
        return decision('align_base', 'base changed; align and independently review again')
    if task.get('head_sha') != snapshot.get('head_sha'):
        return decision('review', 'new commit invalidates previous review')
    verdict = task.get('verdict')
    if verdict == 'changes' or task.get('blocking', 0):
        return decision('revise', 'review requests changes')
    if verdict == 'evidence':
        return decision('gather_evidence', 'review needs evidence')
    if verdict != 'approve':
        return decision('review', 'independent review is not complete')
    if (not task.get('author_run') or not task.get('reviewer_run')
            or task['author_run'] == task['reviewer_run']
            or task.get('coordinator_verified') is not True):
        return decision('escalate', 'coordinator has not verified an independent run')
    if task.get('blocking') != 0 or snapshot.get('review_tail_valid') is not True:
        return decision('review', 'review record or post-review changes are not verified')
    if snapshot.get('mergeable') is False:
        return decision('align_base', 'merge conflict requires changes and re-review')
    check = snapshot.get('checks')
    if check == 'failure':
        return decision('revise', 'required validation failed')
    if check != 'success':
        return decision('wait_checks', 'waiting for exact-head validation', False)
    if snapshot.get('mergeable') is not True:
        return decision('wait_checks', 'GitHub is calculating mergeability', False)
    return decision('merge', 'authorized, reviewed and validated exact version', False)


class GitHub:
    def api(self, path, body=None, method='POST'):
        command = ['gh', 'api', f'repos/{REPOSITORY}/{path}']
        if body is not None:
            command += ['--method', method, '--input', '-']
        result = subprocess.run(command, input=None if body is None else json.dumps(body),
                                text=True, capture_output=True, timeout=45)
        if result.returncode:
            raise RuntimeError(f'GitHub API failed for {path}: {result.stderr[:300]}')
        return json.loads(result.stdout)

    def snapshot(self, task):
        pr = self.api(f'pulls/{int(task["pr"])}')
        result = {'merged': pr['merged'], 'state': pr['state'], 'draft': pr['draft'],
                  'node_id': pr['node_id'], 'base_ref': pr['base']['ref'],
                  'base_sha': pr['base']['sha'], 'head_sha': pr['head']['sha'],
                  'head_repository': (pr['head']['repo'] or {}).get('full_name'),
                  'mergeable': pr['mergeable'], 'files': [], 'checks': 'pending',
                  'review_tail_valid': False}
        if pr['merged'] or pr['state'] != 'open':
            return result
        for page in range(1, 12):
            batch = self.api(f'pulls/{int(task["pr"])}/files?per_page=100&page={page}')
            for entry in batch:
                result['files'].append(entry['filename'])
                if entry.get('previous_filename'):
                    result['files'].append(entry['previous_filename'])
            if len(batch) < 100:
                break
        else:
            raise RuntimeError('PR exceeds controller inspection limit')
        if (task.get('head_sha') == result['head_sha'] and task.get('reviewed_sha')
                and task.get('record_path') and task.get('record_blob')):
            commit = self.api(f'git/commits/{result["head_sha"]}')
            if [p['sha'] for p in commit['parents']] == [task['reviewed_sha']]:
                tail = self.api(f'compare/{task["reviewed_sha"]}...{result["head_sha"]}')
                changed = tail.get('files', [])
                result['review_tail_valid'] = (
                    tail.get('status') == 'ahead' and tail.get('total_commits') == 1
                    and len(changed) == 1 and changed[0]['status'] == 'added'
                    and changed[0]['filename'] == task['record_path']
                    and changed[0]['sha'] == task['record_blob']
                    and task['record_path'].startswith('reviews/'))
        runs = self.api(f'actions/runs?head_sha={result["head_sha"]}&per_page=100')['workflow_runs']
        runs = [r for r in runs if r['path'] == WORKFLOW
                and r['head_sha'] == result['head_sha'] and r['event'] == 'pull_request'
                and any(p['number'] == int(task['pr'])
                        and p['base']['sha'] == result['base_sha']
                        and p['head']['sha'] == result['head_sha']
                        for p in r.get('pull_requests', []))]
        if runs:
            run = max(runs, key=lambda r: (r['id'], r.get('run_attempt', 1)))
            if run['status'] == 'completed':
                result['checks'] = 'success' if run['conclusion'] == 'success' else 'failure'
        return result

    def set_draft(self, node_id, draft):
        mutation = 'convertPullRequestToDraft' if draft else 'markPullRequestReadyForReview'
        query = ('mutation($id:ID!){' + mutation
                 + '(input:{pullRequestId:$id}){pullRequest{id isDraft}}}')
        result = subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + query,
                                 '-f', 'id=' + node_id], text=True, capture_output=True, timeout=45)
        if result.returncode or json.loads(result.stdout).get('errors'):
            raise RuntimeError('Draft/Ready transition failed')

    def merge(self, number, sha):
        result = self.api(f'pulls/{number}/merge', {'sha': sha, 'merge_method': 'merge'}, 'PUT')
        if result.get('merged') is not True:
            raise RuntimeError('GitHub did not confirm merge')
        return result


def _advance(task, github, apply=False):
    snapshot = github.snapshot(task)
    action = evaluate(task, snapshot)
    if not apply or action['stage'] in ('done', 'stop'):
        return action
    if snapshot['draft'] != action['draft']:
        github.set_draft(snapshot['node_id'], action['draft'])
    if action['stage'] == 'merge':
        # Re-read versions and checks immediately before merging; GitHub also checks head SHA.
        fresh = github.snapshot(task)
        action = evaluate(task, fresh)
        if action['stage'] != 'merge':
            if fresh['draft'] != action['draft']:
                github.set_draft(fresh['node_id'], action['draft'])
            return action
        result = github.merge(int(task['pr']), task['head_sha'])
        return {'stage': 'done', 'reason': 'merged', 'merge_sha': result['sha'], 'draft': False}
    return action


def advance(task, github, apply=False):
    try:
        return _advance(task, github, apply)
    except (RuntimeError, subprocess.SubprocessError, ValueError, KeyError):
        # No merge retry after an ambiguous API error. Best effort to return an
        # unmerged PR to Draft; if the network is down this cannot be guaranteed.
        if apply:
            try:
                current = github.snapshot(task)
                if not current['merged'] and current['state'] == 'open' and not current['draft']:
                    github.set_draft(current['node_id'], True)
            except (RuntimeError, subprocess.SubprocessError, ValueError, KeyError):
                pass
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--decision', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    path = args.decision.resolve()
    allowed = (STATE_DIR / 'decisions').resolve()
    if not path.is_relative_to(allowed):
        parser.error('decision must be coordinator-owned state outside the repository')
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with (STATE_DIR / 'controller.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        task = json.loads(path.read_text())
        try:
            result = advance(task, GitHub(), args.apply)
        except (RuntimeError, subprocess.SubprocessError, ValueError, KeyError) as error:
            result = decision('escalate', f'API error; merge not retried: {error}')
        with (STATE_DIR / 'events.jsonl').open('a') as audit:
            audit.write(json.dumps({'pr': task['pr'], 'head': task.get('head_sha'),
                                    'applied': args.apply, **result}, ensure_ascii=False) + '\n')
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()

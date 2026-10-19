import copy
import unittest
from unittest.mock import patch

from scripts import review_controller as controller


def task():
    return {'repository': controller.REPOSITORY, 'pr': 7,
            'authorization': {'auto_advance': True, 'source': 'user task',
                              'paths': ['docs/proposal.md', 'reviews/T7-r1.md']},
            'base_sha': 'a' * 40, 'head_sha': 'b' * 40, 'verdict': 'approve',
            'author_run': 'author', 'reviewer_run': 'reviewer',
            'coordinator_verified': True, 'blocking': 0}


def snapshot():
    return {'merged': False, 'state': 'open', 'draft': True, 'node_id': 'PR7',
            'head_repository': controller.REPOSITORY, 'base_ref': 'main',
            'files': ['docs/proposal.md', 'reviews/T7-r1.md'],
            'base_sha': 'a' * 40, 'head_sha': 'b' * 40,
            'review_tail_valid': True, 'checks': 'success', 'mergeable': True}


def api_fixture():
    candidate = task() | {'reviewed_sha': 'd' * 40, 'record_path': 'reviews/T7-r1.md',
                          'record_blob': 'e' * 40}
    pr = {'merged': False, 'state': 'open', 'draft': True, 'node_id': 'PR7',
          'base': {'ref': 'main', 'sha': candidate['base_sha']}, 'mergeable': True,
          'head': {'sha': candidate['head_sha'], 'repo': {'full_name': controller.REPOSITORY}}}
    run = {'id': 1, 'path': controller.WORKFLOW, 'head_sha': candidate['head_sha'],
           'event': 'pull_request', 'status': 'completed', 'conclusion': 'success',
           'pull_requests': [{'number': 7, 'base': {'sha': candidate['base_sha']},
                              'head': {'sha': candidate['head_sha']}}]}
    tail = {'status': 'ahead', 'total_commits': 1,
            'files': [{'filename': candidate['record_path'], 'status': 'added',
                       'sha': candidate['record_blob']}]}
    responses = {'pulls/7': pr,
                 'pulls/7/files?per_page=100&page=1': [{'filename': f} for f in snapshot()['files']],
                 f'git/commits/{candidate["head_sha"]}': {'parents': [{'sha': candidate['reviewed_sha']}]},
                 f'compare/{candidate["reviewed_sha"]}...{candidate["head_sha"]}': tail,
                 f'actions/runs?head_sha={candidate["head_sha"]}&per_page=100': {'workflow_runs': [run]}}
    return candidate, responses, run, tail


class FakeGitHub:
    def __init__(self, snapshots, fail=None):
        self.snapshots, self.fail = snapshots, fail
        self.calls, self.reads = [], 0
        self.draft = snapshots[0]['draft']

    def snapshot(self, _task):
        self.reads += 1
        self.calls.append(('snapshot', self.reads))
        if self.fail == f'snapshot:{self.reads}':
            raise RuntimeError('API unavailable')
        result = copy.deepcopy(self.snapshots[min(self.reads - 1, len(self.snapshots) - 1)])
        result['draft'] = self.draft
        return result

    def set_draft(self, node_id, draft):
        self.calls.append(('draft', draft))
        if self.fail == 'draft':
            raise RuntimeError('API unavailable')
        self.draft = draft

    def merge(self, number, sha):
        self.calls.append(('merge', number, sha))
        return {'merged': True, 'sha': 'c' * 40}


class ReviewControllerTests(unittest.TestCase):
    def test_authorization_is_required_and_scoped(self):
        for auth in ({}, {'auto_advance': True},
                     {'auto_advance': False, 'source': 'user task', 'paths': []},
                     {'auto_advance': True, 'source': 'user task', 'paths': ['other.md']}):
            with self.subTest(auth=auth):
                candidate = task()
                candidate['authorization'] = auth
                self.assertEqual(controller.evaluate(candidate, snapshot())['stage'], 'escalate')
        candidate = task()
        del candidate['authorization']
        self.assertEqual(controller.evaluate(candidate, snapshot())['stage'], 'escalate')
        for path in ('local/raw.md', 'private/student.md', 'data/raw.csv', 'logs/run.txt'):
            candidate, state = task(), snapshot()
            candidate['authorization']['paths'] = state['files'] = [path]
            self.assertEqual(controller.evaluate(candidate, state)['stage'], 'escalate')

    def test_review_versions_checks_and_conflicts_fail_closed(self):
        cases = [
            ({'repository': 'someone/else'}, {}, 'escalate'),
            ({}, {'head_repository': 'someone/fork'}, 'escalate'),
            ({}, {'base_ref': 'other'}, 'escalate'),
            ({'author_run': 'reviewer'}, {}, 'escalate'),
            ({'coordinator_verified': False}, {}, 'escalate'),
            ({'verdict': 'pending'}, {}, 'review'),
            ({'verdict': 'changes'}, {}, 'revise'),
            ({'verdict': 'evidence'}, {}, 'gather_evidence'),
            ({'blocking': 1}, {}, 'revise'),
            ({'blocking': None}, {}, 'review'),
            ({}, {'head_sha': 'd' * 40}, 'review'),
            ({}, {'base_sha': 'e' * 40}, 'align_base'),
            ({}, {'review_tail_valid': False}, 'review'),
            ({}, {'checks': 'pending'}, 'wait_checks'),
            ({}, {'checks': 'failure'}, 'revise'),
            ({}, {'mergeable': False}, 'align_base'),
            ({}, {'mergeable': False, 'checks': 'pending'}, 'align_base'),
            ({}, {'mergeable': None}, 'wait_checks'),
        ]
        for change, observed, expected in cases:
            with self.subTest(change=change, observed=observed):
                candidate, state = task() | change, snapshot() | observed
                result = controller.evaluate(candidate, state)
                self.assertEqual(result['stage'], expected)
                github = FakeGitHub([state | {'draft': False}])
                self.assertEqual(controller.advance(candidate, github, True)['stage'], expected)
                self.assertFalse(any(call[0] == 'merge' for call in github.calls))
                self.assertEqual(github.draft, result['draft'])

    def test_approval_and_dry_run(self):
        self.assertEqual(controller.evaluate(task(), snapshot())['stage'], 'merge')
        github = FakeGitHub([snapshot()])
        self.assertEqual(controller.advance(task(), github)['stage'], 'merge')
        self.assertEqual(github.calls, [('snapshot', 1)])

    def test_changed_head_or_base_on_second_read_never_merges(self):
        for field, expected in (('head_sha', 'review'), ('base_sha', 'align_base')):
            with self.subTest(field=field):
                github = FakeGitHub([snapshot(), snapshot() | {field: 'd' * 40}])
                self.assertEqual(controller.advance(task(), github, True)['stage'], expected)
                self.assertEqual(github.calls, [('snapshot', 1), ('draft', False),
                                                ('snapshot', 2), ('draft', True)])

    def test_api_errors_before_merge_never_call_merge(self):
        for failure in ('snapshot:1', 'draft', 'snapshot:2'):
            with self.subTest(failure=failure):
                github = FakeGitHub([snapshot()], fail=failure)
                with self.assertRaises(RuntimeError):
                    controller.advance(task(), github, True)
                self.assertFalse(any(call[0] == 'merge' for call in github.calls))
                self.assertTrue(github.draft)
                if failure == 'snapshot:2':
                    self.assertEqual(github.calls[-2:], [('snapshot', 3), ('draft', True)])

    def test_snapshot_requires_matching_pr_head_base_and_workflow(self):
        for mismatch in ('pr', 'base', 'head', 'workflow', 'event', 'missing_pr', None):
            with self.subTest(mismatch=mismatch):
                candidate, responses, run, _ = api_fixture()
                if mismatch == 'pr': run['pull_requests'][0]['number'] = 8
                if mismatch in ('base', 'head'): run['pull_requests'][0][mismatch]['sha'] = 'f' * 40
                if mismatch == 'workflow': run['path'] = 'another-workflow.yml'
                if mismatch == 'event': run['event'] = 'push'
                if mismatch == 'missing_pr': run['pull_requests'] = []
                with patch.object(controller.GitHub, 'api', side_effect=lambda path: responses[path]):
                    observed = controller.GitHub().snapshot(candidate)
                self.assertEqual(observed['checks'], 'pending' if mismatch else 'success')
                self.assertEqual(controller.evaluate(candidate, observed)['stage'],
                                 'wait_checks' if mismatch else 'merge')

    def test_snapshot_rejects_body_changes_or_wrong_review_blob(self):
        for mismatch in ('body', 'blob', None):
            with self.subTest(mismatch=mismatch):
                candidate, responses, _, tail = api_fixture()
                if mismatch == 'body':
                    tail['files'].append({'filename': 'docs/proposal.md', 'status': 'modified'})
                if mismatch == 'blob': tail['files'][0]['sha'] = 'f' * 40
                with patch.object(controller.GitHub, 'api', side_effect=lambda path: responses[path]):
                    observed = controller.GitHub().snapshot(candidate)
                self.assertEqual(observed['review_tail_valid'], mismatch is None)
                self.assertEqual(controller.evaluate(candidate, observed)['stage'],
                                 'review' if mismatch else 'merge')

    def test_success_marks_ready_then_rechecks_then_merges(self):
        github = FakeGitHub([snapshot()])
        result = controller.advance(task(), github, True)
        self.assertEqual(result['stage'], 'done')
        self.assertEqual(result['merge_sha'], 'c' * 40)
        self.assertEqual(github.calls, [('snapshot', 1), ('draft', False),
                                       ('snapshot', 2), ('merge', 7, 'b' * 40)])

    def test_merged_is_idempotent_and_closed_stops(self):
        for state, expected in (({'merged': True}, 'done'), ({'state': 'closed'}, 'stop')):
            with self.subTest(state=state):
                github = FakeGitHub([snapshot() | state])
                for _ in range(2):
                    self.assertEqual(controller.advance(task(), github, True)['stage'], expected)
                self.assertEqual(github.calls, [('snapshot', 1), ('snapshot', 2)])


if __name__ == '__main__':
    unittest.main()

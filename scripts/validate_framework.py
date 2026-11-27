#!/usr/bin/env python3
"""Pathwise v3.1.0 repository static gate validator (pure Python 3 standard library).

Checks:
1. index/manifest.json syntax, schema fields, enums, FW/TPL whitelist,
   43-parent-slot full coverage, L*-***-dd.dd globally unique leaf sub-slots,
   mandatory business parent_slot_id & batch (Batch 1..4), evergreen
   valid_until==null constraint, upstream_ids DAG integrity, and file existence.
2. research/ tree hygiene (no non-.md files), index/master-map.md §2 43-parent
   mandatory table check, §3 full 5-column (slot_id, parent_slot_id, card_id,
   path, batch) strict 3-way 1:1 bijection, pure-stdlib 14-key YAML Frontmatter
   field-by-field parity with manifest.json, bidirectional body upstream/
   downstream link vs upstream_ids graph consistency, and status-aware body
   checks (>=3 H2/H3 headings for all cards; >=3 checkboxes for draft cards).
3. Local relative links across all Markdown files (supports single-level nested
   square brackets in link text, UTF-8 Chinese and URL-encoded paths, and
   requires README.md when a relative link points to a directory).
4. Hard privacy, binary/non-UTF-8 rejection, local absolute path, credential/
   token, personal email, real-name, independent JSON case instance, and
   controlled admissions data leak scan across all repo files.

Exit codes:
  0 - All checks passed (0 failures).
  1 - One or more hard gate checks failed.
  2 - CLI argument or repository path error.
"""

from __future__ import annotations

import argparse
import datetime
import getpass
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote

# ---------------------------------------------------------------------------
# Constants & Schema Rules (v3.1.0)
# ---------------------------------------------------------------------------

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "updated_at",
    "layers",
    "slot_prefixes",
    "items",
}

REQUIRED_LAYERS = {"framework", "L1", "L2", "L3", "L4"}
BUSINESS_LAYERS = {"L1", "L2", "L3", "L4"}

REQUIRED_ITEM_KEYS = {
    "id",
    "slot_id",
    "title",
    "path",
    "layer",
    "stability",
    "valid_until",
    "drivers",
    "major_codes",
    "target_regions",
    "graduation_cohort",
    "upstream_ids",
    "stale_action",
    "status",
}

REQUIRED_BUSINESS_EXTRA_KEYS = {
    "parent_slot_id",
    "batch",
}

REQUIRED_FRONTMATTER_KEYS = {
    "card_id",
    "slot_id",
    "parent_slot_id",
    "layer",
    "batch",
    "status",
    "stability",
    "valid_until",
    "drivers",
    "major_codes",
    "target_regions",
    "graduation_cohort",
    "upstream_ids",
    "last_verified",
}

ALLOWED_LAYERS = {"framework", "L1", "L2", "L3", "L4"}
ALLOWED_STABILITY = {"evergreen", "volatile"}
ALLOWED_DRIVERS = {"policy", "industry", "demography"}
ALLOWED_STATUS = {"active", "draft", "needs_reverify", "deprecated"}
ALLOWED_BATCHES = {"Batch 1", "Batch 2", "Batch 3", "Batch 4"}

ALLOWED_SLOT_PREFIXES = {
    "FW",
    "TPL",
    "L1-POL",
    "L1-IND",
    "L1-DEM",
    "L2-CAR",
    "L3-PTH",
    "L4-DEC",
}

ALLOWED_FRAMEWORK_SLOTS: Set[str] = (
    {f"FW-{i:03d}" for i in range(1, 8)}
    | {f"TPL-{i:03d}" for i in range(1, 6)}
)

ALLOWED_PARENT_SLOTS_BY_LAYER: Dict[str, Set[str]] = {
    "L1": (
        {f"L1-DEM-{i:02d}" for i in range(1, 4)}
        | {f"L1-POL-{i:02d}" for i in range(1, 9)}
        | {f"L1-IND-{i:02d}" for i in range(1, 10)}
    ),
    "L2": {f"L2-CAR-{i:02d}" for i in range(1, 10)},
    "L3": {f"L3-PTH-{i:02d}" for i in range(1, 9)},
    "L4": {f"L4-DEC-{i:02d}" for i in range(1, 7)},
}

EXPECTED_PARENT_SLOTS: Set[str] = (
    ALLOWED_PARENT_SLOTS_BY_LAYER["L1"]
    | ALLOWED_PARENT_SLOTS_BY_LAYER["L2"]
    | ALLOWED_PARENT_SLOTS_BY_LAYER["L3"]
    | ALLOWED_PARENT_SLOTS_BY_LAYER["L4"]
)

LEAF_SLOT_REGEX_BY_LAYER: Dict[str, re.Pattern[str]] = {
    "L1": re.compile(r"^(?:L1-DEM|L1-POL|L1-IND)-\d{2}\.\d{2}$"),
    "L2": re.compile(r"^L2-CAR-\d{2}\.\d{2}$"),
    "L3": re.compile(r"^L3-PTH-\d{2}\.\d{2}$"),
    "L4": re.compile(r"^L4-DEC-\d{2}\.\d{2}$"),
}

LEAF_SLOT_GENERIC_RE = re.compile(r"^(L[1-4]-[A-Z]{3}-\d{2})\.(\d{2})$")

MAJOR_CODE_RE = re.compile(r"^[0-9]{6}[KT]?$")
COHORT_STRUCTURED_RE = re.compile(
    r"^(20\d{2})_in_(20\d{2})_(?:bachelor|5yr|master|phd|md_residency)$"
)
PLACEHOLDER_RE = re.compile(r"(?:[<>[\]]|待填|YYYY|TBD|TODO)")

# Matches §3 leaf sub-slot rows in index/master-map.md:
#   | `L3-PTH-08.01` | `L3-PTH-08` | `card_id` | [title](../research/...) | `Batch 3` | ... |
MASTER_MAP_LEAF_SLOT_ROW_RE = re.compile(
    r"^\|\s*`(L[1-4]-[A-Z]{3}-\d{2}\.\d{2})`\s*\|"
)
# Matches §2 43-parent-slot summary rows (with optional 2-digit index column):
#   | 01 | `L1-DEM-01` | ... |  OR  | `L1-DEM-01` | ... |
MASTER_MAP_PARENT_SLOT_ROW_RE = re.compile(
    r"^\|\s*(?:\d{2}\s*\|\s*)?`(L[1-4]-[A-Z]{3}-\d{2})`\s*\|"
)

# Body upstream / downstream link line prefixes for graph consistency check (#3)
UPSTREAM_BULLET_RE = re.compile(r"^\s*-\s*\*\*(?:前置上游卡片|核心上游卡片)\*\*")
DOWNSTREAM_BULLET_RE = re.compile(r"^\s*-\s*\*\*直接传导下游卡片\*\*")

HEADING_H2_H3_RE = re.compile(r"^#{2,3}\s+\S")
CHECKBOX_ITEM_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+\S")
MIN_OUTLINE_HEADINGS = 3
MIN_OUTLINE_CHECKBOXES = 3

# Salted SHA-256 digests for restricted private identifiers (zero plaintext in repo)
PRIVACY_SALT = "pathwise-v3-privacy-guard:"
RESTRICTED_ASCII_TOKEN_DIGESTS: Set[str] = {
    "126f3f6b4822aea594877ca804223f77819443ceee75c546a8ec9f1ffdbd8999",
}
RESTRICTED_CJK_3GRAM_DIGESTS: Set[str] = {
    "7441e77cfae788709a6698cda0e92028a4ce72f41f47f7dd43ffe774102cf264",
}

GENERIC_SYSTEM_USERS = {
    "root",
    "runner",
    "ubuntu",
    "admin",
    "administrator",
    "user",
    "nobody",
    "vscode",
    "github",
    "actions",
    "docker",
    "guest",
    "daemon",
    "system",
    "test",
}

# Dynamically assembled path prefixes so literal forbidden prefixes never appear in source
_P_USERS = "".join(["Us", "ers"])
_P_VOLUMES = "".join(["Vol", "umes"])
_P_HOME = "".join(["ho", "me"])
_P_DOCSET = " ".join(["Documents", "and", "Settings"])

ABS_PATH_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    (
        "macos_user_or_volume_path",
        re.compile(rf"(?<![A-Za-z0-9_])/(?:{_P_USERS}|{_P_VOLUMES})/"),
    ),
    (
        "linux_home_user_path",
        re.compile(rf"(?<![A-Za-z0-9_])/{_P_HOME}/[A-Za-z0-9._-]+/"),
    ),
    (
        "windows_user_path",
        re.compile(rf"[A-Za-z]:\\(?:{_P_USERS}|{_P_DOCSET})\\"),
    ),
]

EMAIL_RE = re.compile(r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,}))")
ALLOWED_EMAIL_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "users.noreply.github.com",
}

SECRET_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("openai_or_sk_key", re.compile(r"\bsk-[A-Za-z0-9\-_]{20,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("tavily_api_key", re.compile(r"\btvly-[A-Za-z0-9\-_]{16,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    (
        "bearer_token",
        re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/]{24,}=*\b"),
    ),
    (
        "generic_secret_assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{24,}['\"]?"
        ),
    ),
]

FILLED_NAME_FIELD_RE = re.compile(
    r"(?:考生姓名|学生姓名|真实姓名)\s*[:：]\s*(?!(?:待填|示例|占位|匿名|虚构|无|不填|严禁|CASE-|TBD|N/A|\[|<))([\u4e00-\u9fff]{2,4})(?:\s|$|[，。；,;|)])"
)

FORBIDDEN_FILENAME_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("raw_csv_file", re.compile(r"(?i)\.raw\.csv$")),
    ("legacy_data_csv", re.compile(r"(?i)-data\.csv$")),
    ("youzy_artifact", re.compile(r"(?i)youzy")),
    ("individual_case_file", re.compile(r"(?i)individual-case")),
    ("controlled_binary_data_file", re.compile(r"(?i)\.(?:xlsx|parquet|sqlite|db)$")),
    ("controlled_cn_artifact", re.compile(r"(?:招生底表|个案|志愿表)")),
]

JSON_PII_KEYS: Set[str] = {
    "student_name",
    "candidate_name",
    "real_name",
    "id_card",
    "id_number",
    "national_id",
    "phone",
    "mobile",
    "phone_number",
    "wechat",
    "home_address",
}

JSON_CASE_INSTANCE_KEYS: Set[str] = {
    "student_rank",
    "equivalent_score",
    "gaokao_score",
    "exam_score",
    "provincial_rank",
    "subject_combo",
    "max_annual_tuition_cny",
    "grad_school_budget_tolerance",
    "early_low_pay_buffer_years",
    "hard_redline_majors",
    "hard_redline_scenarios",
    "soft_dislike_majors",
    "dim1_academic_physical",
    "dim2_financial_horizon",
    "dim3_preference_boundaries",
    "dim4_consensus_debias",
    "group_evaluations",
    "search_windows",
    "drift_decomposition",
}

JSON_CASE_ID_VAL_RE = re.compile(r"(?i)^CASE-[A-Z0-9_-]+$")

CONTROLLED_DATA_CONTENT_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("youzy_domain_or_dump", re.compile(r"(?i)youzy\.cn|youzy[_-]score|youzy[_-]dump")),
    (
        "legacy_admissions_csv_header",
        re.compile(r"校名\s*,\s*省份\s*,\s*层次\s*,\s*科类\s*,\s*类型\s*,\s*年份\s*,\s*组号\s*,\s*最低分\s*,\s*最低位次"),
    ),
    ("legacy_admissions_dom_marker", re.compile(r",\s*dom=[1-9]\d*\s*,")),
]

# Real GaoKao score CSV data row heuristic (only applied to actual .csv files)
REAL_CSV_SCORE_ROW_RE = re.compile(r"^[^,\n]+,[^,\n]+,(?:985|211|双一流|本科|公办|民办),(?:物理类|历史类),")

# Supports single-level nested square brackets in link label, e.g. [[官方原件] 标题](path.md)
MD_LINK_RE = re.compile(r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`+[^`]*`+")
ASCII_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{3,}")
CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]{3,}")


# ---------------------------------------------------------------------------
# Helpers & Pure-Stdlib YAML Frontmatter Parser
# ---------------------------------------------------------------------------

def is_valid_iso_date(val: object) -> bool:
    if not isinstance(val, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", val):
        return False
    try:
        datetime.date.fromisoformat(val)
        return True
    except ValueError:
        return False


def sha256_salted(token: str) -> str:
    return hashlib.sha256((PRIVACY_SALT + token).encode("utf-8")).hexdigest()


def iter_repo_files(repo_root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in {".git", "__pycache__", ".venv", "venv"}
        )
        for fname in sorted(filenames):
            yield Path(dirpath) / fname


def find_duplicates(seq: Sequence[str]) -> List[str]:
    seen: Set[str] = set()
    dups: List[str] = []
    for item in seq:
        if item in seen and item not in dups:
            dups.append(item)
        seen.add(item)
    return dups


def strip_fenced_code_blocks(text: str) -> List[Tuple[int, str]]:
    """Return (1-based line_no, line_text) outside fenced code blocks."""
    out: List[Tuple[int, str]] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if not in_fence:
            m = re.match(r"^(`{3,}|~{3,})", stripped)
            if m:
                in_fence = True
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                continue
            out.append((idx, line))
        else:
            if re.match(rf"^{re.escape(fence_char)}{{{fence_len},}}\s*$", stripped):
                in_fence = False
                fence_char = ""
                fence_len = 0
    return out


def normalize_link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")].strip()
    else:
        target = target.split()[0] if target.split() else ""
    return target


def resolve_local_md_link(
    base_dir: Path,
    repo_root: Path,
    raw_target: str,
) -> Tuple[Optional[str], Optional[str]]:
    """Resolve a Markdown link target to repo-relative POSIX path, or return (None, err)."""
    target = normalize_link_target(raw_target)
    if not target:
        return None, "empty link target"
    lower = target.lower()
    if lower.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#")):
        return None, "external or anchor link"
    path_part = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not path_part:
        return None, "empty path part"
    if path_part.startswith("/") or re.match(r"^[A-Za-z]:\\", path_part):
        return None, f"disallowed absolute link target '{target}'"
    root_resolved = repo_root.resolve()
    resolved = (base_dir / path_part).resolve()
    try:
        rel = resolved.relative_to(root_resolved).as_posix()
    except ValueError:
        return None, f"link escapes repository root '{target}'"
    return rel, None


def _strip_yaml_inline_comment(raw: str) -> str:
    """Strip trailing '# ...' comments outside single/double quotes."""
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(raw):
        if escaped:
            escaped = False
            continue
        if in_double:
            if ch == "\\":
                escaped = True
            elif ch == '"':
                in_double = False
        elif in_single:
            if ch == "'":
                in_single = False
        else:
            if ch == '"':
                in_double = True
            elif ch == "'":
                in_single = True
            elif ch == "#" and (idx == 0 or raw[idx - 1].isspace()):
                return raw[:idx].rstrip()
    return raw.rstrip()


def _parse_yaml_scalar(raw: str) -> Tuple[Any, Optional[str]]:
    val = raw.strip()
    if not val:
        return None, None
    if val.startswith('"'):
        try:
            return json.loads(val), None
        except json.JSONDecodeError as exc:
            return None, f"invalid double-quoted string {val!r} ({exc})"
    if val.startswith("'"):
        if len(val) >= 2 and val.endswith("'"):
            return val[1:-1].replace("''", "'"), None
        return None, f"unterminated single-quoted string {val!r}"
    low = val.lower()
    if low in {"null", "~"}:
        return None, None
    if low == "true":
        return True, None
    if low == "false":
        return False, None
    return val, None


def _split_yaml_inline_list(inner: str) -> Tuple[List[Any], Optional[str]]:
    items: List[Any] = []
    cur: List[str] = []
    in_single = False
    in_double = False
    escaped = False

    for ch in inner:
        if escaped:
            cur.append(ch)
            escaped = False
            continue
        if in_double:
            cur.append(ch)
            if ch == "\\":
                escaped = True
            elif ch == '"':
                in_double = False
        elif in_single:
            cur.append(ch)
            if ch == "'":
                in_single = False
        else:
            if ch == '"':
                in_double = True
                cur.append(ch)
            elif ch == "'":
                in_single = True
                cur.append(ch)
            elif ch == ",":
                token = "".join(cur).strip()
                if not token:
                    return [], "empty element in inline YAML list"
                parsed, err = _parse_yaml_scalar(token)
                if err:
                    return [], err
                items.append(parsed)
                cur = []
            else:
                cur.append(ch)

    if in_single or in_double:
        return [], "unterminated quote inside inline YAML list"

    tail = "".join(cur).strip()
    if tail:
        parsed, err = _parse_yaml_scalar(tail)
        if err:
            return [], err
        items.append(parsed)
    return items, None


def _parse_yaml_value(raw: str) -> Tuple[Any, Optional[str]]:
    cleaned = _strip_yaml_inline_comment(raw).strip()
    if not cleaned:
        return None, None
    if cleaned.startswith("["):
        if not cleaned.endswith("]"):
            return None, f"unterminated inline YAML list: {cleaned!r}"
        try:
            loaded = json.loads(cleaned)
            if isinstance(loaded, list):
                return loaded, None
        except json.JSONDecodeError:
            pass
        inner = cleaned[1:-1].strip()
        if not inner:
            return [], None
        return _split_yaml_inline_list(inner)
    return _parse_yaml_scalar(cleaned)


def parse_markdown_frontmatter(
    text: str,
) -> Tuple[Optional[Dict[str, Any]], str, int, List[str]]:
    """Parse top-of-file YAML frontmatter (pure stdlib).

    Returns (data, body, body_start_line_no, errors).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, 1, ["missing opening YAML frontmatter delimiter '---' on line 1"]

    end_idx: Optional[int] = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() in {"---", "..."}:
            end_idx = idx
            break

    if end_idx is None:
        return None, text, 1, ["missing closing YAML frontmatter delimiter '---'"]

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    body_start_line_no = end_idx + 2
    data: Dict[str, Any] = {}
    errors: List[str] = []

    i = 0
    while i < len(fm_lines):
        raw_line = fm_lines[i]
        line_no = i + 2
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        if raw_line[0].isspace() or stripped.startswith("-"):
            errors.append(f"line {line_no}: unexpected indentation or stray list item in YAML frontmatter")
            i += 1
            continue

        key, sep, rest = raw_line.partition(":")
        if not sep:
            errors.append(f"line {line_no}: malformed YAML frontmatter line (missing ':')")
            i += 1
            continue

        key = key.strip()
        if not key:
            errors.append(f"line {line_no}: empty YAML frontmatter key")
            i += 1
            continue
        if key in data:
            errors.append(f"line {line_no}: duplicate YAML frontmatter key '{key}'")

        rest_clean = _strip_yaml_inline_comment(rest).strip()
        if rest_clean == "":
            block_items: List[Any] = []
            j = i + 1
            found_block_list = False
            while j < len(fm_lines):
                sub_raw = fm_lines[j]
                sub_strip = sub_raw.strip()
                if not sub_strip or sub_strip.startswith("#"):
                    j += 1
                    continue
                if re.match(r"^\s*-\s+", sub_raw) or sub_strip == "-":
                    found_block_list = True
                    item_text = re.sub(r"^\s*-\s*", "", sub_raw, count=1)
                    item_val, err = _parse_yaml_value(item_text)
                    if err:
                        errors.append(f"line {j + 2}: key '{key}' list item error: {err}")
                    else:
                        block_items.append(item_val)
                    j += 1
                else:
                    break
            if found_block_list:
                data[key] = block_items
                i = j
                continue
            data[key] = None
            i += 1
            continue

        val, err = _parse_yaml_value(rest)
        if err:
            errors.append(f"line {line_no}: key '{key}' parse error: {err}")
        else:
            data[key] = val
        i += 1

    return data, body, body_start_line_no, errors


def find_placeholders_in_value(val: Any) -> List[str]:
    hits: List[str] = []
    if isinstance(val, str):
        if PLACEHOLDER_RE.search(val):
            hits.append(val)
    elif isinstance(val, list):
        for elem in val:
            hits.extend(find_placeholders_in_value(elem))
    return hits


def _strip_code_ticks(cell: str) -> str:
    s = cell.strip()
    if len(s) >= 2 and s.startswith("`") and s.endswith("`"):
        return s[1:-1].strip()
    return s


def parse_master_map_slots(
    repo_root: Path,
) -> Tuple[
    Optional[Dict[str, Dict[str, Any]]],
    List[str],
    Set[str],
    List[str],
    List[str],
]:
    """Parse index/master-map.md §2 parent table and §3 leaf 5-tuple rows.

    Returns (leaf_rows_by_slot, dup_leaf_slots, parent_slot_set, dup_parent_slots, errors).
    """
    master_map = repo_root / "index" / "master-map.md"
    if not master_map.is_file():
        return None, [], set(), [], ["[tree] Missing required file: index/master-map.md"]
    try:
        text = master_map.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, [], set(), [], [f"[tree] index/master-map.md is not valid UTF-8 ({exc})"]

    leaf_list: List[str] = []
    leaf_rows: Dict[str, Dict[str, Any]] = {}
    parent_list: List[str] = []
    errors: List[str] = []
    index_dir = master_map.parent

    for line_no, line in strip_fenced_code_blocks(text):
        stripped = line.strip()
        m_leaf = MASTER_MAP_LEAF_SLOT_ROW_RE.match(stripped)
        if m_leaf:
            slot_id = m_leaf.group(1)
            leaf_list.append(slot_id)
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", stripped.strip("|"))]
            if len(cells) < 5:
                errors.append(
                    f"[tree] index/master-map.md:{line_no}: leaf row '{slot_id}' has fewer than 5 table columns"
                )
                continue
            col_slot = _strip_code_ticks(cells[0])
            col_parent = _strip_code_ticks(cells[1])
            col_card_id = _strip_code_ticks(cells[2])
            col_link_cell = cells[3]
            col_batch = _strip_code_ticks(cells[4])

            link_match = MD_LINK_RE.search(col_link_cell)
            col_path: Optional[str] = None
            if not link_match:
                errors.append(
                    f"[tree] index/master-map.md:{line_no}: leaf row '{slot_id}' column 4 missing Markdown link"
                )
            else:
                rel_path, link_err = resolve_local_md_link(index_dir, repo_root, link_match.group(1))
                if link_err is not None or rel_path is None:
                    errors.append(
                        f"[tree] index/master-map.md:{line_no}: leaf row '{slot_id}' invalid link ({link_err})"
                    )
                else:
                    col_path = rel_path

            if slot_id not in leaf_rows:
                leaf_rows[slot_id] = {
                    "slot_id": col_slot,
                    "parent_slot_id": col_parent,
                    "card_id": col_card_id,
                    "path": col_path,
                    "batch": col_batch,
                    "line_no": line_no,
                }
            continue

        m_parent = MASTER_MAP_PARENT_SLOT_ROW_RE.match(stripped)
        if m_parent:
            parent_list.append(m_parent.group(1))

    dup_leaves = find_duplicates(leaf_list)
    dup_parents = find_duplicates(parent_list)
    return leaf_rows, dup_leaves, set(parent_list), dup_parents, errors


def scan_json_for_case_content(rel: str, text: str) -> List[str]:
    failures: List[str] = []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"[privacy] {rel}: invalid JSON file in public repository ({exc})"]

    found_case_id_key = False
    found_pii_keys: Set[str] = set()
    found_case_keys: Set[str] = set()
    found_case_id_val = False

    def walk(node: object) -> None:
        nonlocal found_case_id_key, found_case_id_val
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(k, str):
                    kl = k.lower()
                    if kl == "case_id":
                        found_case_id_key = True
                    if kl in JSON_PII_KEYS:
                        found_pii_keys.add(k)
                    if kl in JSON_CASE_INSTANCE_KEYS:
                        found_case_keys.add(k)
                walk(v)
        elif isinstance(node, list):
            for elem in node:
                walk(elem)
        elif isinstance(node, str):
            if JSON_CASE_ID_VAL_RE.fullmatch(node.strip()):
                found_case_id_val = True

    walk(payload)

    if found_case_id_key or found_case_id_val:
        failures.append(
            f"[privacy] {rel}: detected individual case identifier ('case_id' / CASE-*) in JSON file"
        )
    if found_pii_keys:
        failures.append(
            f"[privacy] {rel}: detected personal identity key(s) in JSON file: {sorted(found_pii_keys)}"
        )
    if len(found_case_keys) >= 2:
        failures.append(
            f"[privacy] {rel}: detected individual case/calculation instance JSON keys ({sorted(found_case_keys)})"
        )
    return failures


def load_blocklist(cli_path: Optional[str]) -> List[str]:
    terms: List[str] = []
    source = cli_path or os.environ.get("PATHWISE_PRIVACY_BLOCKLIST")
    if not source:
        return terms
    p = Path(source).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"Blocklist file not found: {source}")
    for line in p.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if item and not item.startswith("#"):
            terms.append(item)
    return terms


def collect_runtime_os_usernames() -> Set[str]:
    candidates: Set[str] = set()
    for val in (
        getpass.getuser(),
        Path.home().name,
        os.environ.get("USER", ""),
        os.environ.get("LOGNAME", ""),
    ):
        cleaned = (val or "").strip()
        if len(cleaned) >= 4 and cleaned.lower() not in GENERIC_SYSTEM_USERS:
            candidates.add(cleaned)
    return candidates


# ---------------------------------------------------------------------------
# Check 1: index/manifest.json (v3.1.0 Parent + Leaf Sub-Slot Gate)
# ---------------------------------------------------------------------------

def check_manifest(
    repo_root: Path,
) -> Tuple[List[str], int, List[Dict[str, Any]]]:
    failures: List[str] = []
    business_items: List[Dict[str, Any]] = []
    manifest_path = repo_root / "index" / "manifest.json"
    if not manifest_path.is_file():
        return ["[manifest] Missing required file: index/manifest.json"], 0, []

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"[manifest] Invalid JSON in index/manifest.json: {exc}"], 0, []

    if not isinstance(data, dict):
        return ["[manifest] Top-level JSON value must be an object."], 0, []

    missing_top = sorted(REQUIRED_TOP_LEVEL_KEYS - set(data.keys()))
    if missing_top:
        failures.append(f"[manifest] Missing top-level keys: {missing_top}")

    if not isinstance(data.get("schema_version"), str) or not data["schema_version"].strip():
        failures.append("[manifest] 'schema_version' must be a non-empty string.")

    if not is_valid_iso_date(data.get("updated_at")):
        failures.append("[manifest] 'updated_at' must be a valid YYYY-MM-DD ISO date.")

    layers = data.get("layers")
    if not isinstance(layers, dict):
        failures.append("[manifest] 'layers' must be an object.")
    else:
        missing_layers = sorted(REQUIRED_LAYERS - set(layers.keys()))
        if missing_layers:
            failures.append(f"[manifest] 'layers' missing required keys: {missing_layers}")

    slot_prefixes = data.get("slot_prefixes")
    valid_prefixes: Set[str] = set()
    if not isinstance(slot_prefixes, dict) or not slot_prefixes:
        failures.append("[manifest] 'slot_prefixes' must be a non-empty object.")
    else:
        for k, v in slot_prefixes.items():
            if not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip():
                failures.append(f"[manifest] Invalid slot_prefixes entry: {k!r}")
            else:
                valid_prefixes.add(k)
        unknown_prefixes = sorted(valid_prefixes - ALLOWED_SLOT_PREFIXES)
        if unknown_prefixes:
            failures.append(
                f"[manifest] 'slot_prefixes' contains disallowed/deprecated prefix(es): {unknown_prefixes}"
            )
        missing_prefixes = sorted(ALLOWED_SLOT_PREFIXES - valid_prefixes)
        if missing_prefixes:
            failures.append(
                f"[manifest] 'slot_prefixes' missing required prefix(es): {missing_prefixes}"
            )

    items = data.get("items")
    if not isinstance(items, list):
        failures.append("[manifest] 'items' must be an array.")
        return failures, 0, []

    seen_ids: Set[str] = set()
    seen_slots: Dict[str, str] = {}
    seen_paths: Dict[str, str] = {}
    seen_framework_slots: Set[str] = set()
    covered_parents: Set[str] = set()
    upstream_graph: Dict[str, List[str]] = {}

    for idx, item in enumerate(items):
        label = f"items[{idx}]"
        if not isinstance(item, dict):
            failures.append(f"[manifest] {label} must be an object.")
            continue

        missing_keys = sorted(REQUIRED_ITEM_KEYS - set(item.keys()))
        if missing_keys:
            failures.append(f"[manifest] {label} missing required fields: {missing_keys}")
            continue

        item_id = item["id"]
        if not isinstance(item_id, str) or not item_id.strip():
            failures.append(f"[manifest] {label}.id must be a non-empty string.")
            continue
        label = f"item '{item_id}'"
        if item_id in seen_ids:
            failures.append(f"[manifest] Duplicate item id: '{item_id}'")
        seen_ids.add(item_id)

        layer = item["layer"]
        if layer not in ALLOWED_LAYERS:
            failures.append(f"[manifest] {label}.layer '{layer}' not in {sorted(ALLOWED_LAYERS)}.")

        if layer in BUSINESS_LAYERS:
            business_items.append(item)
            missing_biz = sorted(REQUIRED_BUSINESS_EXTRA_KEYS - set(item.keys()))
            if missing_biz:
                failures.append(
                    f"[manifest] {label} (layer '{layer}') missing mandatory business field(s): {missing_biz}"
                )
            if "batch" in item:
                if not isinstance(item["batch"], str) or item["batch"] not in ALLOWED_BATCHES:
                    failures.append(
                        f"[manifest] {label}.batch '{item['batch']}' not in {sorted(ALLOWED_BATCHES)}."
                    )

        slot_id = item["slot_id"]
        if not isinstance(slot_id, str) or not slot_id.strip():
            failures.append(f"[manifest] {label}.slot_id must be a non-empty string.")
        else:
            if valid_prefixes and not any(
                slot_id == p or slot_id.startswith(p + "-") for p in valid_prefixes
            ):
                failures.append(
                    f"[manifest] {label}.slot_id '{slot_id}' does not match any prefix in slot_prefixes."
                )

            if layer == "framework":
                if slot_id not in ALLOWED_FRAMEWORK_SLOTS:
                    failures.append(
                        f"[manifest] {label}.slot_id '{slot_id}' is not in FW-001..007 / TPL-001..005 whitelist."
                    )
                else:
                    seen_framework_slots.add(slot_id)
            elif layer in BUSINESS_LAYERS:
                leaf_re = LEAF_SLOT_REGEX_BY_LAYER[layer]
                if not leaf_re.fullmatch(slot_id):
                    failures.append(
                        f"[manifest] {label}.slot_id '{slot_id}' does not match v3.1 leaf sub-slot regex for layer '{layer}'."
                    )
                else:
                    parent_prefix = slot_id.split(".", 1)[0]
                    if parent_prefix not in ALLOWED_PARENT_SLOTS_BY_LAYER[layer]:
                        failures.append(
                            f"[manifest] {label}.slot_id '{slot_id}' parent '{parent_prefix}' "
                            f"is not in the 43-parent-slot whitelist for layer '{layer}'."
                        )
                    else:
                        covered_parents.add(parent_prefix)
                    if "parent_slot_id" in item:
                        if not isinstance(item["parent_slot_id"], str) or item["parent_slot_id"] != parent_prefix:
                            failures.append(
                                f"[manifest] {label}.parent_slot_id '{item['parent_slot_id']}' "
                                f"must strictly equal '{parent_prefix}'."
                            )

            if slot_id in seen_slots:
                failures.append(
                    f"[manifest] Duplicate slot_id '{slot_id}': already claimed by item '{seen_slots[slot_id]}' (conflict at {label})."
                )
            else:
                seen_slots[slot_id] = item_id

        if not isinstance(item["title"], str) or not item["title"].strip():
            failures.append(f"[manifest] {label}.title must be a non-empty string.")

        rel_path = item["path"]
        if not isinstance(rel_path, str) or not rel_path.strip():
            failures.append(f"[manifest] {label}.path must be a non-empty string.")
        elif rel_path.startswith("/") or "\\" in rel_path or ".." in Path(rel_path).parts:
            failures.append(f"[manifest] {label}.path '{rel_path}' must be a clean repo-relative POSIX path.")
        else:
            if rel_path in seen_paths:
                failures.append(
                    f"[manifest] Duplicate path '{rel_path}': already claimed by item '{seen_paths[rel_path]}' (conflict at {label})."
                )
            else:
                seen_paths[rel_path] = item_id
            target = (repo_root / rel_path).resolve()
            try:
                target.relative_to(repo_root.resolve())
            except ValueError:
                failures.append(f"[manifest] {label}.path '{rel_path}' escapes repository root.")
            else:
                if not target.is_file():
                    failures.append(f"[manifest] {label}.path does not exist on disk: {rel_path}")

        stability = item["stability"]
        if stability not in ALLOWED_STABILITY:
            failures.append(f"[manifest] {label}.stability '{stability}' not in {sorted(ALLOWED_STABILITY)}.")

        valid_until = item["valid_until"]
        if stability == "volatile":
            if not is_valid_iso_date(valid_until):
                failures.append(
                    f"[manifest] {label} is volatile so 'valid_until' must be a valid YYYY-MM-DD date."
                )
        elif stability == "evergreen":
            if valid_until is not None:
                failures.append(
                    f"[manifest] {label} is evergreen so 'valid_until' must strictly be null (got {valid_until!r})."
                )

        drivers = item["drivers"]
        if not isinstance(drivers, list) or any(
            not isinstance(d, str) or d not in ALLOWED_DRIVERS for d in drivers
        ):
            failures.append(
                f"[manifest] {label}.drivers must be a list of {sorted(ALLOWED_DRIVERS)}."
            )
        else:
            if layer in BUSINESS_LAYERS and len(drivers) == 0:
                failures.append(f"[manifest] {label}.drivers must be non-empty for layer '{layer}'.")
            dup_drivers = find_duplicates(drivers)
            if dup_drivers:
                failures.append(f"[manifest] {label}.drivers contains duplicate entries: {dup_drivers}")

        major_codes = item["major_codes"]
        if not isinstance(major_codes, list) or any(
            not isinstance(c, str) or not MAJOR_CODE_RE.fullmatch(c) for c in major_codes
        ):
            failures.append(
                f"[manifest] {label}.major_codes entries must match ^[0-9]{{6}}[KT]?$."
            )
        else:
            dup_majors = find_duplicates(major_codes)
            if dup_majors:
                failures.append(f"[manifest] {label}.major_codes contains duplicate entries: {dup_majors}")

        target_regions = item["target_regions"]
        if (
            not isinstance(target_regions, list)
            or len(target_regions) == 0
            or any(not isinstance(r, str) or not r.strip() for r in target_regions)
        ):
            failures.append(
                f"[manifest] {label}.target_regions must be a non-empty list of non-empty strings."
            )
        else:
            bad_placeholders = [r for r in target_regions if PLACEHOLDER_RE.search(r)]
            if bad_placeholders:
                failures.append(
                    f"[manifest] {label}.target_regions contains placeholder text: {bad_placeholders}"
                )
            dup_regions = find_duplicates(target_regions)
            if dup_regions:
                failures.append(f"[manifest] {label}.target_regions contains duplicate entries: {dup_regions}")

        graduation_cohort = item["graduation_cohort"]
        if (
            not isinstance(graduation_cohort, list)
            or len(graduation_cohort) == 0
            or any(not isinstance(c, str) or not c.strip() for c in graduation_cohort)
        ):
            failures.append(
                f"[manifest] {label}.graduation_cohort must be a non-empty list of cohort identifiers."
            )
        else:
            dup_cohorts = find_duplicates(graduation_cohort)
            if dup_cohorts:
                failures.append(
                    f"[manifest] {label}.graduation_cohort contains duplicate entries: {dup_cohorts}"
                )
            if "all_cohorts" in graduation_cohort:
                if graduation_cohort != ["all_cohorts"]:
                    failures.append(
                        f"[manifest] {label}.graduation_cohort cannot mix 'all_cohorts' with specific cohorts."
                    )
            else:
                for c in graduation_cohort:
                    if PLACEHOLDER_RE.search(c):
                        failures.append(
                            f"[manifest] {label}.graduation_cohort contains placeholder text: '{c}'"
                        )
                        continue
                    m = COHORT_STRUCTURED_RE.fullmatch(c)
                    if not m:
                        failures.append(
                            f"[manifest] {label}.graduation_cohort entry '{c}' must be 'all_cohorts' "
                            "or match ^20\\d{2}_in_20\\d{2}_(?:bachelor|5yr|master|phd|md_residency)$."
                        )
                    else:
                        intake_yr, grad_yr = int(m.group(1)), int(m.group(2))
                        if grad_yr <= intake_yr:
                            failures.append(
                                f"[manifest] {label}.graduation_cohort entry '{c}' has grad_year <= intake_year."
                            )

        upstream_ids = item["upstream_ids"]
        if not isinstance(upstream_ids, list) or any(
            not isinstance(u, str) or not u.strip() for u in upstream_ids
        ):
            failures.append(f"[manifest] {label}.upstream_ids must be a list of non-empty strings.")
        else:
            dup_upstreams = find_duplicates(upstream_ids)
            if dup_upstreams:
                failures.append(
                    f"[manifest] {label}.upstream_ids contains duplicate entries: {dup_upstreams}"
                )
            upstream_graph[item_id] = list(upstream_ids)

        if not isinstance(item["stale_action"], str) or not item["stale_action"].strip():
            failures.append(f"[manifest] {label}.stale_action must be a non-empty string.")

        if item["status"] not in ALLOWED_STATUS:
            failures.append(f"[manifest] {label}.status '{item['status']}' not in {sorted(ALLOWED_STATUS)}.")

    # 12-framework-slot full coverage gate (FW-001..007 / TPL-001..005 mandatory in v3.1.0)
    if seen_framework_slots != ALLOWED_FRAMEWORK_SLOTS:
        missing_fw = sorted(ALLOWED_FRAMEWORK_SLOTS - seen_framework_slots)
        extra_fw = sorted(seen_framework_slots - ALLOWED_FRAMEWORK_SLOTS)
        failures.append(
            f"[manifest] Incomplete 12-framework-slot coverage (FW-001..007 / TPL-001..005): "
            f"missing={missing_fw}, extra={extra_fw}"
        )

    # Non-empty business items + 43-parent-slot full coverage gate (mandatory in v3.1.0)
    if len(business_items) == 0:
        failures.append(
            "[manifest] Business items (L1-L4) must be non-empty in v3.1.0."
        )
    missing_parents = sorted(EXPECTED_PARENT_SLOTS - covered_parents)
    if missing_parents:
        failures.append(
            f"[manifest] Incomplete 43-parent-slot coverage: missing {len(missing_parents)} parent slot(s): {missing_parents}"
        )

    # Upstream reference integrity + cycle check
    for item_id, upstreams in upstream_graph.items():
        for uid in upstreams:
            if uid == item_id:
                failures.append(f"[manifest] item '{item_id}' cannot reference itself in upstream_ids.")
            elif uid not in seen_ids:
                failures.append(
                    f"[manifest] item '{item_id}' references unknown upstream_id: '{uid}'."
                )

    # 3-color DFS cycle detection (0=unvisited, 1=visiting, 2=done)
    color: Dict[str, int] = {node: 0 for node in upstream_graph}

    def dfs(node: str, stack: List[str]) -> None:
        color[node] = 1
        for nxt in upstream_graph.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == 1:
                cycle = " -> ".join(stack[stack.index(nxt) :] + [nxt])
                failures.append(f"[manifest] Dependency cycle detected in upstream_ids: {cycle}")
            elif color[nxt] == 0:
                dfs(nxt, stack + [nxt])
        color[node] = 2

    for node in list(upstream_graph.keys()):
        if color[node] == 0:
            dfs(node, [node])

    return failures, len(items), business_items


# ---------------------------------------------------------------------------
# Check 2: research/ Tree, 3-Way 5-Tuple Bijection, YAML, Graph & Outlines
# ---------------------------------------------------------------------------

def check_research_tree_and_cards(
    repo_root: Path,
    business_items: Sequence[Dict[str, Any]],
) -> Tuple[List[str], int, int]:
    failures: List[str] = []
    research_dir = repo_root / "research"
    disk_leaf_paths: Set[str] = set()

    if not research_dir.is_dir():
        return ["[tree] Missing required directory: research/"], 0, 0

    # 2.1 Scan research/ for leaf .md cards and disallow any non-.md stray file
    for path in iter_repo_files(research_dir):
        rel = path.relative_to(repo_root).as_posix()
        if path.suffix.lower() != ".md":
            failures.append(
                f"[tree] {rel}: disallowed non-.md file under research/ (only Markdown cards and README.md allowed)"
            )
            continue
        if path.name == "README.md":
            continue
        disk_leaf_paths.add(rel)

    # 2.2 Parse index/master-map.md §2 43-parent table & §3 leaf 5-tuple rows
    (
        master_leaf_rows,
        dup_master_leaves,
        master_parent_slots,
        dup_master_parents,
        map_errors,
    ) = parse_master_map_slots(repo_root)
    failures.extend(map_errors)
    if dup_master_leaves:
        failures.append(
            f"[tree] index/master-map.md contains duplicate leaf slot_id row(s): {dup_master_leaves}"
        )
    if dup_master_parents:
        failures.append(
            f"[tree] index/master-map.md §2 contains duplicate parent slot_id row(s): {dup_master_parents}"
        )
    # Unconditional 43-parent-slot check (zero-match short-circuit removed)
    if master_leaf_rows is not None and master_parent_slots != EXPECTED_PARENT_SLOTS:
        extra_p = sorted(master_parent_slots - EXPECTED_PARENT_SLOTS)
        missing_p = sorted(EXPECTED_PARENT_SLOTS - master_parent_slots)
        failures.append(
            "[tree] index/master-map.md §2 parent-slot summary table diverges from 43-slot whitelist "
            f"(matched={len(master_parent_slots)}, extra={extra_p}, missing={missing_p})"
        )

    # 2.3 Strict 3-way 1:1 full-column bijection: D (disk) <-> J (manifest) <-> M (master-map)
    j_by_path: Dict[str, Dict[str, Any]] = {}
    j_by_slot: Dict[str, Dict[str, Any]] = {}
    for item in business_items:
        p = item.get("path")
        s = item.get("slot_id")
        if isinstance(p, str):
            j_by_path[p] = item
        if isinstance(s, str):
            j_by_slot[s] = item

    j_paths = set(j_by_path.keys())
    j_slots = set(j_by_slot.keys())

    if disk_leaf_paths != j_paths:
        unregistered = sorted(disk_leaf_paths - j_paths)
        ghosts = sorted(j_paths - disk_leaf_paths)
        if unregistered:
            failures.append(
                f"[tree] Unregistered leaf .md card(s) under research/ missing from index/manifest.json: {unregistered}"
            )
        if ghosts:
            failures.append(
                f"[tree] Manifest business item path(s) missing on disk under research/ (or named README.md): {ghosts}"
            )

    if master_leaf_rows is not None:
        master_leaf_slots = set(master_leaf_rows.keys())
        if master_leaf_slots != j_slots:
            extra_m = sorted(master_leaf_slots - j_slots)
            missing_m = sorted(j_slots - master_leaf_slots)
            if extra_m:
                failures.append(
                    f"[tree] index/master-map.md lists leaf slot_id(s) absent from index/manifest.json: {extra_m}"
                )
            if missing_m:
                failures.append(
                    f"[tree] index/manifest.json business leaf slot_id(s) missing from index/master-map.md: {missing_m}"
                )

        # Full 5-tuple row-by-row parity between master-map.md §3 and manifest.json
        for slot_id in sorted(master_leaf_slots & j_slots):
            row = master_leaf_rows[slot_id]
            m_item = j_by_slot[slot_id]
            ln = row["line_no"]
            expected_parent = slot_id.split(".", 1)[0]
            if row["parent_slot_id"] != expected_parent or row["parent_slot_id"] != m_item.get("parent_slot_id"):
                failures.append(
                    f"[tree] index/master-map.md:{ln} slot '{slot_id}': parent_slot_id {row['parent_slot_id']!r} "
                    f"!= manifest {m_item.get('parent_slot_id')!r}"
                )
            if row["card_id"] != m_item.get("id"):
                failures.append(
                    f"[tree] index/master-map.md:{ln} slot '{slot_id}': card_id {row['card_id']!r} "
                    f"!= manifest id {m_item.get('id')!r}"
                )
            if row["path"] != m_item.get("path"):
                failures.append(
                    f"[tree] index/master-map.md:{ln} slot '{slot_id}': link path {row['path']!r} "
                    f"!= manifest path {m_item.get('path')!r}"
                )
            if row["batch"] != m_item.get("batch"):
                failures.append(
                    f"[tree] index/master-map.md:{ln} slot '{slot_id}': batch {row['batch']!r} "
                    f"!= manifest batch {m_item.get('batch')!r}"
                )

    # 2.4 Leaf card 14-key YAML Frontmatter parity, status-aware body & graph link check
    for rel in sorted(disk_leaf_paths):
        card_path = repo_root / rel
        try:
            text = card_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"[card] {rel}: failed to decode as UTF-8 ({exc})")
            continue

        fm, body, body_start_line, parse_errors = parse_markdown_frontmatter(text)
        for err in parse_errors:
            failures.append(f"[card] {rel}: YAML frontmatter error: {err}")

        m_item = j_by_path.get(rel)

        if fm is not None:
            missing_fm = sorted(REQUIRED_FRONTMATTER_KEYS - set(fm.keys()))
            if missing_fm:
                failures.append(f"[card] {rel}: YAML frontmatter missing required key(s): {missing_fm}")

            for k in sorted(REQUIRED_FRONTMATTER_KEYS & set(fm.keys())):
                ph_hits = find_placeholders_in_value(fm[k])
                if ph_hits:
                    failures.append(
                        f"[card] {rel}: YAML frontmatter field '{k}' contains forbidden placeholder text: {ph_hits}"
                    )

            if "batch" in fm:
                if not isinstance(fm["batch"], str) or fm["batch"] not in ALLOWED_BATCHES:
                    failures.append(
                        f"[card] {rel}: YAML frontmatter 'batch' {fm['batch']!r} not in {sorted(ALLOWED_BATCHES)}."
                    )

            if "last_verified" in fm:
                if not is_valid_iso_date(fm["last_verified"]):
                    failures.append(
                        f"[card] {rel}: YAML frontmatter 'last_verified' must be a valid YYYY-MM-DD ISO date."
                    )

            if "stability" in fm and "valid_until" in fm:
                if fm["stability"] == "volatile" and not is_valid_iso_date(fm["valid_until"]):
                    failures.append(
                        f"[card] {rel}: YAML frontmatter stability=='volatile' requires valid YYYY-MM-DD valid_until."
                    )
                elif fm["stability"] == "evergreen" and fm["valid_until"] is not None:
                    failures.append(
                        f"[card] {rel}: YAML frontmatter stability=='evergreen' requires valid_until==null "
                        f"(got {fm['valid_until']!r})."
                    )

            fm_slot = fm.get("slot_id")
            fm_parent = fm.get("parent_slot_id")
            fm_layer = fm.get("layer")
            if isinstance(fm_slot, str):
                m_leaf = LEAF_SLOT_GENERIC_RE.fullmatch(fm_slot)
                if not m_leaf:
                    failures.append(
                        f"[card] {rel}: YAML frontmatter slot_id '{fm_slot}' is not a valid L*-***-dd.dd leaf sub-slot."
                    )
                else:
                    expected_parent = m_leaf.group(1)
                    if fm_parent != expected_parent:
                        failures.append(
                            f"[card] {rel}: YAML frontmatter parent_slot_id '{fm_parent}' "
                            f"must strictly equal '{expected_parent}'."
                        )
                    if isinstance(fm_layer, str) and fm_layer in ALLOWED_PARENT_SLOTS_BY_LAYER:
                        if expected_parent not in ALLOWED_PARENT_SLOTS_BY_LAYER[fm_layer]:
                            failures.append(
                                f"[card] {rel}: YAML frontmatter parent_slot_id '{expected_parent}' "
                                f"does not belong to layer '{fm_layer}'."
                            )

            # Field-by-field parity against manifest.json item
            if m_item is not None:
                parity_pairs = [
                    ("card_id", "id"),
                    ("slot_id", "slot_id"),
                    ("parent_slot_id", "parent_slot_id"),
                    ("layer", "layer"),
                    ("batch", "batch"),
                    ("status", "status"),
                    ("stability", "stability"),
                    ("valid_until", "valid_until"),
                    ("drivers", "drivers"),
                    ("major_codes", "major_codes"),
                    ("target_regions", "target_regions"),
                    ("graduation_cohort", "graduation_cohort"),
                    ("upstream_ids", "upstream_ids"),
                ]
                for fm_key, m_key in parity_pairs:
                    if fm_key in fm and m_key in m_item and fm[fm_key] != m_item[m_key]:
                        failures.append(
                            f"[card] {rel}: YAML '{fm_key}' ({fm[fm_key]!r}) != manifest '{m_key}' ({m_item[m_key]!r})"
                        )

        # Status-aware body check (#1):
        #   - H2/H3 headings >= 3 required for all statuses
        #   - '- [ ]' checkboxes >= 3 required ONLY for draft outline cards
        body_lines = strip_fenced_code_blocks(body)
        heading_count = sum(1 for _ln, line in body_lines if HEADING_H2_H3_RE.match(line))
        checkbox_count = sum(1 for _ln, line in body_lines if CHECKBOX_ITEM_RE.match(line))

        if heading_count < MIN_OUTLINE_HEADINGS:
            failures.append(
                f"[card] {rel}: body has only {heading_count} H2/H3 heading(s); minimum required is {MIN_OUTLINE_HEADINGS}"
            )
        card_status = fm.get("status") if fm is not None else "draft"
        if card_status == "draft" and checkbox_count < MIN_OUTLINE_CHECKBOXES:
            failures.append(
                f"[card] {rel}: draft card body has only {checkbox_count} '- [ ]' checklist item(s); "
                f"minimum required is {MIN_OUTLINE_CHECKBOXES}"
            )

        # Bidirectional body upstream/downstream link vs upstream_ids graph check (#3)
        if m_item is not None:
            cur_id = m_item.get("id")
            cur_upstreams = set(m_item.get("upstream_ids", [])) if isinstance(m_item.get("upstream_ids"), list) else set()
            for rel_ln, line in body_lines:
                abs_ln = body_start_line + rel_ln - 1
                is_up_line = bool(UPSTREAM_BULLET_RE.match(line))
                is_down_line = bool(DOWNSTREAM_BULLET_RE.match(line))
                if not (is_up_line or is_down_line):
                    continue
                cleaned_line = INLINE_CODE_RE.sub("", line)
                for match in MD_LINK_RE.finditer(cleaned_line):
                    target_rel, link_err = resolve_local_md_link(card_path.parent, repo_root, match.group(1))
                    if link_err is not None or target_rel is None:
                        continue
                    target_item = j_by_path.get(target_rel)
                    if target_item is None:
                        continue
                    target_id = target_item.get("id")
                    if is_up_line:
                        if isinstance(target_id, str) and target_id not in cur_upstreams:
                            failures.append(
                                f"[graph] {rel}:{abs_ln}: body upstream link to '{target_rel}' "
                                f"(card_id='{target_id}') is missing from YAML/manifest upstream_ids"
                            )
                    elif is_down_line:
                        target_upstreams = (
                            set(target_item.get("upstream_ids", []))
                            if isinstance(target_item.get("upstream_ids"), list)
                            else set()
                        )
                        if isinstance(cur_id, str) and cur_id not in target_upstreams:
                            failures.append(
                                f"[graph] {rel}:{abs_ln}: body downstream link to '{target_rel}' "
                                f"(card_id='{target_id}') is missing reverse upstream_id '{cur_id}' in target card"
                            )

    master_count = len(master_leaf_rows) if master_leaf_rows is not None else 0
    return failures, len(disk_leaf_paths), master_count


# ---------------------------------------------------------------------------
# Check 3: Markdown local relative links
# ---------------------------------------------------------------------------

def check_markdown_links(repo_root: Path) -> Tuple[List[str], int, int]:
    failures: List[str] = []
    md_files = 0
    checked_links = 0
    root_resolved = repo_root.resolve()

    for path in iter_repo_files(repo_root):
        if path.suffix.lower() != ".md":
            continue
        md_files += 1
        rel_md = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"[links] {rel_md}: failed to decode as UTF-8 ({exc})")
            continue

        for line_no, line in strip_fenced_code_blocks(text):
            cleaned_line = INLINE_CODE_RE.sub("", line)
            for match in MD_LINK_RE.finditer(cleaned_line):
                target = normalize_link_target(match.group(1))
                if not target:
                    continue
                lower = target.lower()
                if lower.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#")):
                    continue

                checked_links += 1
                path_part = target.split("#", 1)[0].split("?", 1)[0]
                path_part = unquote(path_part)
                if not path_part:
                    continue

                if path_part.startswith("/") or re.match(r"^[A-Za-z]:\\", path_part):
                    failures.append(
                        f"[links] {rel_md}:{line_no}: disallowed absolute link target '{target}'"
                    )
                    continue

                resolved = (path.parent / path_part).resolve()
                try:
                    resolved.relative_to(root_resolved)
                except ValueError:
                    failures.append(
                        f"[links] {rel_md}:{line_no}: link escapes repository root '{target}'"
                    )
                    continue

                if not resolved.exists():
                    failures.append(
                        f"[links] {rel_md}:{line_no}: broken relative link '{target}'"
                    )
                elif resolved.is_dir() and not (resolved / "README.md").is_file():
                    failures.append(
                        f"[links] {rel_md}:{line_no}: directory link target '{target}' has no README.md index"
                    )

    return failures, md_files, checked_links


# ---------------------------------------------------------------------------
# Check 4: Privacy, Path, Credential & Controlled-Data Leak Scan
# ---------------------------------------------------------------------------

def check_privacy_and_leaks(
    repo_root: Path,
    extra_blocklist: Sequence[str],
) -> Tuple[List[str], int]:
    failures: List[str] = []
    scanned_files = 0
    runtime_usernames = collect_runtime_os_usernames()
    extra_lower = [t.lower() for t in extra_blocklist]

    for path in iter_repo_files(repo_root):
        scanned_files += 1
        rel = path.relative_to(repo_root).as_posix()

        # 4.1 Forbidden filename check
        for rule_name, pat in FORBIDDEN_FILENAME_PATTERNS:
            if pat.search(path.name):
                failures.append(f"[privacy] {rel}: forbidden controlled/private filename ({rule_name})")

        # Read file bytes: reject binary (NUL byte) and non-UTF-8 files by default
        raw = path.read_bytes()
        is_binary_or_bad_utf8 = False
        if b"\x00" in raw:
            failures.append(f"[privacy] {rel}: disallowed binary file containing NUL byte")
            is_binary_or_bad_utf8 = True
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"[privacy] {rel}: disallowed non-UTF-8 encoded file ({exc})")
            is_binary_or_bad_utf8 = True
            text = raw.decode("utf-8", errors="ignore")

        # 4.1b JSON individual-case / filled-instance content scan (all .json except index/manifest.json)
        if not is_binary_or_bad_utf8 and path.suffix.lower() == ".json" and rel != "index/manifest.json":
            failures.extend(scan_json_for_case_content(rel, text))

        is_gitignore = path.name == ".gitignore"
        csv_real_rows = 0

        for line_no, line in enumerate(text.splitlines(), start=1):
            # 4.2 Local absolute path check
            for rule_name, pat in ABS_PATH_PATTERNS:
                if pat.search(line):
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected local absolute path ({rule_name})"
                    )

            # 4.3 Dynamic runtime OS username check
            line_lower = line.lower()
            for uname in runtime_usernames:
                if uname.lower() in line_lower:
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected local OS username identifier"
                    )
                    break

            # 4.4 Hashed restricted ASCII token check (CI-safe fallback)
            for tok in ASCII_TOKEN_RE.findall(line):
                if sha256_salted(tok.lower()) in RESTRICTED_ASCII_TOKEN_DIGESTS:
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected restricted private handle"
                    )
                    break

            # 4.5 Hashed restricted CJK 3-gram check (catches legacy v1 real case name)
            cjk_hit = False
            for run in CJK_RUN_RE.findall(line):
                for i in range(len(run) - 2):
                    if sha256_salted(run[i : i + 3]) in RESTRICTED_CJK_3GRAM_DIGESTS:
                        failures.append(
                            f"[privacy] {rel}:{line_no}: detected restricted real personal name"
                        )
                        cjk_hit = True
                        break
                if cjk_hit:
                    break

            # 4.6 Filled personal name field heuristic
            if FILLED_NAME_FIELD_RE.search(line):
                failures.append(
                    f"[privacy] {rel}:{line_no}: detected filled real personal name field"
                )

            # 4.7 External blocklist terms
            for term_raw, term_low in zip(extra_blocklist, extra_lower):
                if term_low in line_lower:
                    failures.append(
                        f"[privacy] {rel}:{line_no}: matched external privacy blocklist term (len={len(term_raw)})"
                    )
                    break

            # 4.8 Personal email check
            for email_match in EMAIL_RE.finditer(line):
                domain = email_match.group(2).lower()
                if domain not in ALLOWED_EMAIL_DOMAINS:
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected non-example email address (domain={domain})"
                    )

            # 4.9 API Key / Token / Private key check
            for rule_name, pat in SECRET_PATTERNS:
                if pat.search(line):
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected credential/token pattern ({rule_name})"
                    )

            # 4.10 Controlled commercial admissions data content check
            if not is_gitignore:
                for rule_name, pat in CONTROLLED_DATA_CONTENT_PATTERNS:
                    if pat.search(line):
                        failures.append(
                            f"[privacy] {rel}:{line_no}: detected controlled admissions dataset marker ({rule_name})"
                        )

            if path.suffix.lower() == ".csv" and REAL_CSV_SCORE_ROW_RE.search(line):
                csv_real_rows += 1

        if path.suffix.lower() == ".csv" and csv_real_rows >= 3:
            failures.append(
                f"[privacy] {rel}: detected {csv_real_rows} rows of real admissions score CSV data"
            )

    return failures, scanned_files


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Validate Pathwise v3.1.0 repository manifest, fine-grained tree, YAML frontmatter, links, and privacy boundaries."
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=str(default_root),
        help="Repository root directory (defaults to parent of scripts/).",
    )
    parser.add_argument(
        "--blocklist-file",
        default=None,
        help="Optional external file with extra sensitive terms (one per line; must stay outside public repo).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(f"ERROR: Repository root directory not found: {repo_root}", file=sys.stderr)
        return 2

    try:
        extra_blocklist = load_blocklist(args.blocklist_file)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    manifest_failures, manifest_items, business_items = check_manifest(repo_root)
    tree_failures, disk_leaves, map_leaves = check_research_tree_and_cards(repo_root, business_items)
    link_failures, md_files, checked_links = check_markdown_links(repo_root)
    privacy_failures, scanned_files = check_privacy_and_leaks(repo_root, extra_blocklist)

    all_failures = manifest_failures + tree_failures + link_failures + privacy_failures

    print("=== Pathwise v3.1.0 Static Framework Gate ===")
    print(
        f"[1/4] Manifest & slot gate: total_items={manifest_items}, "
        f"business_items={len(business_items)}, failures={len(manifest_failures)}"
    )
    print(
        f"[2/4] Research tree, 3-way bijection & card gate: "
        f"disk_leaves={disk_leaves}, master_map_leaves={map_leaves}, "
        f"manifest_leaves={len(business_items)}, failures={len(tree_failures)}"
    )
    print(
        f"[3/4] Markdown relative links: md_files={md_files}, "
        f"local_links_checked={checked_links}, failures={len(link_failures)}"
    )
    print(
        f"[4/4] Privacy & controlled-data leak scan: files_scanned={scanned_files}, "
        f"failures={len(privacy_failures)}"
    )

    if all_failures:
        print("\n--- Failure Details ---")
        for msg in all_failures:
            print(f"FAIL: {msg}")
        print(f"\nRESULT: FAIL (total_failures={len(all_failures)})")
        return 1

    print("\nRESULT: PASS (total_failures=0)")
    print(
        "NOTE: Static gate checks structure, 3-way 5-tuple bijection, 14-key YAML parity, "
        "graph consistency, link targets, and leak boundaries only; semantic and "
        "source-verification review remains with Red Team and Independent Audit."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

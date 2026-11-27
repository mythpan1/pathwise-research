#!/usr/bin/env python3
"""Pathwise v3 repository static gate validator (pure Python 3 standard library).

Checks:
1. index/manifest.json syntax, schema fields, enums, upstream_ids DAG integrity,
   and target file existence.
2. Local relative links across all Markdown files (ignoring external URLs,
   anchors, fenced code blocks, and inline code spans).
3. Hard privacy, local absolute path, credential/token, personal email,
   real-name, and controlled admissions data leak scan across all repo files.

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
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote

# ---------------------------------------------------------------------------
# Constants & Schema Rules
# ---------------------------------------------------------------------------

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "updated_at",
    "layers",
    "slot_prefixes",
    "items",
}

REQUIRED_LAYERS = {"framework", "L1", "L2", "L3", "L4"}

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

ALLOWED_LAYERS = {"framework", "L1", "L2", "L3", "L4"}
ALLOWED_STABILITY = {"evergreen", "volatile"}
ALLOWED_DRIVERS = {"policy", "industry", "demography"}
ALLOWED_STATUS = {"active", "draft", "needs_reverify", "deprecated"}

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

ALLOWED_SLOTS_BY_LAYER: Dict[str, Set[str]] = {
    "framework": (
        {f"FW-{i:03d}" for i in range(1, 8)}
        | {f"TPL-{i:03d}" for i in range(1, 6)}
    ),
    "L1": (
        {f"L1-DEM-{i:02d}" for i in range(1, 4)}
        | {f"L1-POL-{i:02d}" for i in range(1, 9)}
        | {f"L1-IND-{i:02d}" for i in range(1, 10)}
    ),
    "L2": {f"L2-CAR-{i:02d}" for i in range(1, 10)},
    "L3": {f"L3-PTH-{i:02d}" for i in range(1, 9)},
    "L4": {f"L4-DEC-{i:02d}" for i in range(1, 7)},
}

EXPECTED_BUSINESS_SLOTS: Set[str] = (
    ALLOWED_SLOTS_BY_LAYER["L1"]
    | ALLOWED_SLOTS_BY_LAYER["L2"]
    | ALLOWED_SLOTS_BY_LAYER["L3"]
    | ALLOWED_SLOTS_BY_LAYER["L4"]
)

MAJOR_CODE_RE = re.compile(r"^[0-9]{6}[KT]?$")
COHORT_STRUCTURED_RE = re.compile(
    r"^(20\d{2})_in_(20\d{2})_(?:bachelor|5yr|master|phd|md_residency)$"
)
PLACEHOLDER_RE = re.compile(r"(?:[<>[\]]|待填|YYYY|TBD|TODO)")
MASTER_MAP_SLOT_ROW_RE = re.compile(r"^\|\s*`(L[1-4]-[A-Z]{3}-\d{2})`\s*\|")

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

MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`+[^`]*`+")
ASCII_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{3,}")
CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]{3,}")


# ---------------------------------------------------------------------------
# Helpers
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


def parse_master_map_slots(repo_root: Path) -> Optional[Set[str]]:
    master_map = repo_root / "index" / "master-map.md"
    if not master_map.is_file():
        return None
    try:
        text = master_map.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    slots: Set[str] = set()
    for line in text.splitlines():
        m = MASTER_MAP_SLOT_ROW_RE.match(line.strip())
        if m:
            slots.add(m.group(1))
    return slots


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
# Check 1: index/manifest.json
# ---------------------------------------------------------------------------

def check_manifest(repo_root: Path) -> Tuple[List[str], int]:
    failures: List[str] = []
    manifest_path = repo_root / "index" / "manifest.json"
    if not manifest_path.is_file():
        return [f"[manifest] Missing required file: index/manifest.json"], 0

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"[manifest] Invalid JSON in index/manifest.json: {exc}"], 0

    if not isinstance(data, dict):
        return ["[manifest] Top-level JSON value must be an object."], 0

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

    master_map_slots = parse_master_map_slots(repo_root)
    if master_map_slots is not None and master_map_slots != EXPECTED_BUSINESS_SLOTS:
        extra_in_map = sorted(master_map_slots - EXPECTED_BUSINESS_SLOTS)
        missing_in_map = sorted(EXPECTED_BUSINESS_SLOTS - master_map_slots)
        failures.append(
            "[manifest] master-map.md business slot_id set diverges from 43-slot whitelist "
            f"(extra={extra_in_map}, missing={missing_in_map})"
        )

    items = data.get("items")
    if not isinstance(items, list):
        failures.append("[manifest] 'items' must be an array.")
        return failures, 0

    seen_ids: Set[str] = set()
    seen_slots: Dict[str, str] = {}
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

        slot_id = item["slot_id"]
        layer = item["layer"]
        if layer not in ALLOWED_LAYERS:
            failures.append(f"[manifest] {label}.layer '{layer}' not in {sorted(ALLOWED_LAYERS)}.")

        if not isinstance(slot_id, str) or not slot_id.strip():
            failures.append(f"[manifest] {label}.slot_id must be a non-empty string.")
        else:
            if valid_prefixes and not any(
                slot_id == p or slot_id.startswith(p + "-") for p in valid_prefixes
            ):
                failures.append(
                    f"[manifest] {label}.slot_id '{slot_id}' does not match any prefix in slot_prefixes."
                )
            if layer in ALLOWED_SLOTS_BY_LAYER and slot_id not in ALLOWED_SLOTS_BY_LAYER[layer]:
                failures.append(
                    f"[manifest] {label}.slot_id '{slot_id}' is not in the controlled whitelist for layer '{layer}'."
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
        else:
            if valid_until is not None and not is_valid_iso_date(valid_until):
                failures.append(
                    f"[manifest] {label}.valid_until must be null or a valid YYYY-MM-DD date."
                )

        drivers = item["drivers"]
        if not isinstance(drivers, list) or any(
            not isinstance(d, str) or d not in ALLOWED_DRIVERS for d in drivers
        ):
            failures.append(
                f"[manifest] {label}.drivers must be a list of {sorted(ALLOWED_DRIVERS)}."
            )
        else:
            if layer in {"L1", "L2", "L3", "L4"} and len(drivers) == 0:
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
                cycle = " -> ".join(stack[stack.index(nxt):] + [nxt])
                failures.append(f"[manifest] Dependency cycle detected in upstream_ids: {cycle}")
            elif color[nxt] == 0:
                dfs(nxt, stack + [nxt])
        color[node] = 2

    for node in list(upstream_graph.keys()):
        if color[node] == 0:
            dfs(node, [node])

    return failures, len(items)


# ---------------------------------------------------------------------------
# Check 2: Markdown local relative links
# ---------------------------------------------------------------------------

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
        target = target[1:target.index(">")].strip()
    else:
        # Strip optional markdown link title: path/to/file.md "title"
        target = target.split()[0] if target.split() else ""
    return target


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

    return failures, md_files, checked_links


# ---------------------------------------------------------------------------
# Check 3: Privacy, Path, Credential & Controlled-Data Leak Scan
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

        # 3.1 Forbidden filename check
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

        # 3.1b JSON individual-case / filled-instance content scan (all .json except index/manifest.json)
        if not is_binary_or_bad_utf8 and path.suffix.lower() == ".json" and rel != "index/manifest.json":
            failures.extend(scan_json_for_case_content(rel, text))

        is_gitignore = path.name == ".gitignore"
        csv_real_rows = 0

        for line_no, line in enumerate(text.splitlines(), start=1):
            # 3.2 Local absolute path check
            for rule_name, pat in ABS_PATH_PATTERNS:
                if pat.search(line):
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected local absolute path ({rule_name})"
                    )

            # 3.3 Dynamic runtime OS username check
            line_lower = line.lower()
            for uname in runtime_usernames:
                if uname.lower() in line_lower:
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected local OS username identifier"
                    )
                    break

            # 3.4 Hashed restricted ASCII token check (CI-safe fallback)
            for tok in ASCII_TOKEN_RE.findall(line):
                if sha256_salted(tok.lower()) in RESTRICTED_ASCII_TOKEN_DIGESTS:
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected restricted private handle"
                    )
                    break

            # 3.5 Hashed restricted CJK 3-gram check (catches legacy v1 real case name)
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

            # 3.6 Filled personal name field heuristic
            if FILLED_NAME_FIELD_RE.search(line):
                failures.append(
                    f"[privacy] {rel}:{line_no}: detected filled real personal name field"
                )

            # 3.7 External blocklist terms
            for term_raw, term_low in zip(extra_blocklist, extra_lower):
                if term_low in line_lower:
                    failures.append(
                        f"[privacy] {rel}:{line_no}: matched external privacy blocklist term (len={len(term_raw)})"
                    )
                    break

            # 3.8 Personal email check
            for email_match in EMAIL_RE.finditer(line):
                domain = email_match.group(2).lower()
                if domain not in ALLOWED_EMAIL_DOMAINS:
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected non-example email address (domain={domain})"
                    )

            # 3.9 API Key / Token / Private key check
            for rule_name, pat in SECRET_PATTERNS:
                if pat.search(line):
                    failures.append(
                        f"[privacy] {rel}:{line_no}: detected credential/token pattern ({rule_name})"
                    )

            # 3.10 Controlled commercial admissions data content check
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
        description="Validate Pathwise v3 repository manifest, relative links, and privacy/leak boundaries."
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

    manifest_failures, manifest_items = check_manifest(repo_root)
    link_failures, md_files, checked_links = check_markdown_links(repo_root)
    privacy_failures, scanned_files = check_privacy_and_leaks(repo_root, extra_blocklist)

    all_failures = manifest_failures + link_failures + privacy_failures

    print("=== Pathwise v3 Static Framework Gate ===")
    print(f"[1/3] Manifest check: items={manifest_items}, failures={len(manifest_failures)}")
    print(
        f"[2/3] Markdown relative links: md_files={md_files}, local_links_checked={checked_links}, failures={len(link_failures)}"
    )
    print(
        f"[3/3] Privacy & controlled-data leak scan: files_scanned={scanned_files}, failures={len(privacy_failures)}"
    )

    if all_failures:
        print("\n--- Failure Details ---")
        for msg in all_failures:
            print(f"FAIL: {msg}")
        print(f"\nRESULT: FAIL (total_failures={len(all_failures)})")
        return 1

    print("\nRESULT: PASS (total_failures=0)")
    print(
        "NOTE: Static gate checks structure, link targets, and leak boundaries only; "
        "semantic and source-verification review remains with Red Team and Independent Audit."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

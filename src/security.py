"""Pre-screen for the manual security checklist (D2 Step 5).

This only FLAGS candidates so the reviewer knows where to look. The graded audit
is still the human review recorded in results/security_audit.csv.
"""
import re
from typing import Dict

CHECKS = {
    "stacked_statement": "Stray semicolon suggesting a second statement",
    "tautology": "Always-true condition (e.g. OR 1=1) that bypasses a filter",
    "comment_marker": "Inline comment (-- or /* */) that could truncate the query",
    "union_select": "Unexpected UNION SELECT pulling from another table",
}

_TAUTOLOGY = re.compile(
    r"\bOR\s+(?:(\d+)\s*=\s*\1\b|'([^']*)'\s*=\s*'\2'|TRUE\b)", re.IGNORECASE
)


def _strip_string_literals(sql: str) -> str:
    return re.sub(r"'(?:[^']|'')*'", "''", sql)


def prescreen(sql: str) -> Dict[str, bool]:
    body = _strip_string_literals(sql).strip()
    return {
        "stacked_statement": ";" in body.rstrip("; \n\t"),
        "tautology": bool(_TAUTOLOGY.search(sql)),
        "comment_marker": "--" in body or "/*" in body,
        "union_select": bool(re.search(r"\bUNION\b(\s+ALL)?\s+SELECT\b", body, re.IGNORECASE)),
    }

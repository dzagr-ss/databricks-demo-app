import re

BLOCKED_SQL_KEYWORDS = [
    "alter",
    "create",
    "delete",
    "drop",
    "grant",
    "insert",
    "merge",
    "revoke",
    "truncate",
    "update",
]


def readonly_sql(query: str) -> bool:
    cleaned = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)
    cleaned = re.sub(r"--.*?$", "", cleaned, flags=re.MULTILINE).strip().lower()
    return (cleaned.startswith("select") or cleaned.startswith("with")) and not any(
        re.search(rf"\b{word}\b", cleaned) for word in BLOCKED_SQL_KEYWORDS
    )

# language: Python 3.11 — parser.py
import re

LINE_RE = re.compile(r"^\s*([^:\s]+):(\S+)\s*$")


def parse_combos(text: str) -> list[tuple[str, str]]:
    out = []
    seen = set()
    for line in text.splitlines():
        m = LINE_RE.match(line)
        if not m:
            continue
        email = m.group(1).strip()
        pw = m.group(2).strip()
        key = (email.lower(), pw)
        if key in seen:
            continue
        seen.add(key)
        out.append((email, pw))
    return out


def parse_single(combo: str):
    m = LINE_RE.match(combo)
    if not m:
        return None
    return m.group(1).strip(), m.group(2).strip()

"""
Statement Normalizer
-----------------------
Normalizes common surface variations of the same mathematical statement so
downstream pattern matchers don't need to handle every spelling. This is
regex-based, controlled normalization -- NOT free-form NLP. If a sentence
uses phrasing outside what's normalized here, the pattern matchers simply
won't match, and the statement correctly falls through to NEEDS_REVIEW
rather than being silently misinterpreted.
"""

import re


def _sup2(m):
    return f"{m.group(1)}\u00b2"


def _sup3(m):
    return f"{m.group(1)}\u00b3"


def normalize(text: str) -> str:
    if not text:
        return ""

    t = text.strip()
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')

    # var^2 / var squared -> var\u00b2
    t = re.sub(r"\b([a-zA-Z])\s*\^\s*2\b", _sup2, t)
    t = re.sub(r"\b([a-zA-Z])\s+squared\b", _sup2, t, flags=re.IGNORECASE)

    # var^3 / var cubed -> var\u00b3
    t = re.sub(r"\b([a-zA-Z])\s*\^\s*3\b", _sup3, t)
    t = re.sub(r"\b([a-zA-Z])\s+cubed\b", _sup3, t, flags=re.IGNORECASE)

    # sqrt notations -> \u221a (use the literal character in the replacement,
    # since Python's re replacement strings don't support \uXXXX escapes)
    ROOT = "\u221a"
    t = re.sub(r"sqrt\(\s*(\d+)\s*\)", ROOT + r"\1", t, flags=re.IGNORECASE)
    t = re.sub(r"\bsqrt\s+(\d+)\b", ROOT + r"\1", t, flags=re.IGNORECASE)
    t = re.sub(r"\broot\s+(\d+)\b", ROOT + r"\1", t, flags=re.IGNORECASE)

    # collapse whitespace
    t = re.sub(r"\s+", " ", t)
    return t.strip()

from __future__ import annotations

import re


_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_URL = re.compile(r"https?://[\w\-\.:/%#\?=&~+,@!$'()*;]+", re.I)
_UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I
)
_TOKEN = re.compile(
    r"\b(sk|key|token|secret|passwd|password|api[_-]?key)[=: ]+\S+", re.I
)
_LONGNUM = re.compile(r"\b\d{6,}\b")


def redact_text(text: str, mask: str = "<REDACTED>") -> str:
    if not text:
        return text
    s = text
    s = _EMAIL.sub("<EMAIL>", s)
    s = _URL.sub("<URL>", s)
    s = _UUID.sub("<UUID>", s)
    s = _TOKEN.sub(lambda m: m.group(0).split("=")[0].split(":")[0] + f"={mask}", s)
    s = _LONGNUM.sub("<NUMBER>", s)
    return s

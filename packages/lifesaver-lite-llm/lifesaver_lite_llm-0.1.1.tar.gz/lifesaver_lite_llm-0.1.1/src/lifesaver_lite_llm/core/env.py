from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def parse_env_line(line: str) -> Tuple[str, str] | None:
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    if "=" not in s:
        return None
    key, val = s.split("=", 1)
    key = key.strip()
    val = val.strip().strip("'\"")
    return key, val


def load_dotenv(path: str | Path = ".env") -> Dict[str, str]:
    p = Path(path)
    loaded: Dict[str, str] = {}
    if not p.exists():
        return loaded
    for line in p.read_text(encoding="utf-8").splitlines():
        kv = parse_env_line(line)
        if kv is None:
            continue
        k, v = kv
        if k and v and k not in os.environ:
            os.environ[k] = v
            loaded[k] = v
    return loaded


def missing_env(keys: Iterable[str]) -> List[str]:
    return [k for k in keys if not os.environ.get(k)]

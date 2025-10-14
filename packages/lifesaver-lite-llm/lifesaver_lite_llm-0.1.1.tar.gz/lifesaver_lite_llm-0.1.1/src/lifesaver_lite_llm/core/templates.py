from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


REPLACERS = [
    (re.compile(r"https?://\S+"), "<URL>"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<EMAIL>"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "<DATE>"),
    (re.compile(r"\b\d{2}:\d{2}(:\d{2})?\b"), "<TIME>"),
    (re.compile(r"\b\d+[.]\d+\b"), "<NUMBER>"),
    (re.compile(r"\b\d+\b"), "<NUMBER>"),
    (
        re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
            re.I,
        ),
        "<UUID>",
    ),
]


def normalize_prompt(p: str) -> str:
    s = p.strip()
    # Remove duplicate whitespace
    s = re.sub(r"\s+", " ", s)
    for pat, repl in REPLACERS:
        s = pat.sub(repl, s)
    return s


def extract_templates(
    prompts: List[str], min_support: int = 2
) -> List[Dict[str, object]]:
    buckets: Dict[str, List[str]] = defaultdict(list)
    for p in prompts:
        if not p or not p.strip():
            continue
        key = normalize_prompt(p)
        buckets[key].append(p)

    items: List[Tuple[str, List[str]]] = [
        (k, v) for k, v in buckets.items() if len(v) >= min_support
    ]
    items.sort(key=lambda kv: len(kv[1]), reverse=True)

    results: List[Dict[str, object]] = []
    for norm, examples in items:
        # Estimate variable slots by counting placeholders
        slot_counts = Counter(re.findall(r"<([A-Z]+)>", norm))
        results.append(
            {
                "template": norm,
                "occurrences": len(examples),
                "slots": dict(slot_counts),
                "examples": examples[:3],  # top few examples
            }
        )
    return results

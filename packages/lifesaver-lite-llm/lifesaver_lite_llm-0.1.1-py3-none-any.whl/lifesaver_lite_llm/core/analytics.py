from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Tuple


def tokenize(text: str) -> List[str]:
    # Very simple tokenization: lowercase, split on non-alphanum
    out = []
    buff = []
    for ch in text.lower():
        if ch.isalnum() or ch in {"_"}:
            buff.append(ch)
        else:
            if buff:
                out.append("".join(buff))
                buff = []
    if buff:
        out.append("".join(buff))
    return out


def ngrams(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def analyze_requests(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(rows)
    total = len(rows)
    by_model = Counter(r.get("model", "") or "unknown" for r in rows)
    tokens_in = [int(r.get("tokens_in", 0)) for r in rows]
    tokens_out = [int(r.get("tokens_out", 0)) for r in rows]
    latency = [int(r.get("latency_ms", 0)) for r in rows]

    def avg(xs: List[int]) -> float:
        return sum(xs) / len(xs) if xs else 0.0

    # top unigrams/bigrams from prompts
    uni = Counter()
    bi = Counter()
    for r in rows:
        ts = tokenize(r.get("input_text", ""))
        uni.update(ts)
        bi.update(ngrams(ts, 2))

    return {
        "total": total,
        "by_model": by_model,
        "avg_tokens_in": avg(tokens_in),
        "avg_tokens_out": avg(tokens_out),
        "avg_latency_ms": avg(latency),
        "top_tokens": uni.most_common(20),
        "top_bigrams": [(" ".join(k), v) for k, v in bi.most_common(20)],
    }

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def _avg(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _estimate_cost(row: Dict[str, Any], providers: Dict[str, Any]) -> float:
    model = (row.get("model") or "").lower()
    tokens_in = int(row.get("tokens_in", 0))
    tokens_out = int(row.get("tokens_out", 0))
    for pid, meta in providers.items():
        if meta.get("match", "").lower() in model and meta.get("pricing"):
            pin = meta["pricing"].get("input_per_1k", 0.0) / 1000.0
            pout = meta["pricing"].get("output_per_1k", 0.0) / 1000.0
            return tokens_in * pin + tokens_out * pout
    return 0.0


def build_suggestions(
    rows: Iterable[Dict[str, Any]], providers: Dict[str, Any]
) -> Dict[str, Any]:
    rows = list(rows)
    costs = [_estimate_cost(r, providers) for r in rows]
    avg_cost = _avg(costs)
    avg_in = _avg([int(r.get("tokens_in", 0)) for r in rows])
    avg_out = _avg([int(r.get("tokens_out", 0)) for r in rows])

    routing_rules: List[str] = []
    tips: List[str] = []

    # Heuristic routing suggestions
    cheap = sorted(
        providers.items(),
        key=lambda kv: kv[1].get("pricing", {}).get("input_per_1k", 1e9),
    )
    if cheap:
        routing_rules.append(
            f"Use {cheap[0][0]} for short/simple tasks (tokens_in < 200)."
        )

    best_quality = sorted(
        providers.items(), key=lambda kv: -float(kv[1].get("quality", 0))
    )
    if best_quality:
        routing_rules.append(
            f"Route complex/code or multi-step tasks to {best_quality[0][0]}."
        )

    if avg_out > avg_in * 0.9:
        tips.append(
            "High output-to-input ratio detected; tighten prompts and prefer streaming or lower-temp."
        )
    if avg_cost > 0.01:  # arbitrary threshold
        tips.append(
            "Average request cost is elevated; prefer compact context and reuse retrieved facts."
        )
    tips.append(
        "Adopt reusable prompt templates with placeholders (<URL>, <NUMBER>) to reduce churn."
    )

    return {
        "avg_cost": avg_cost,
        "routing_rules": routing_rules,
        "tips": tips,
    }

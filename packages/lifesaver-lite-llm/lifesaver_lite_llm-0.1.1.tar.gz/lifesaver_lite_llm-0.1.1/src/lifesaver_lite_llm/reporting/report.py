from __future__ import annotations

from typing import Any, Dict, List


def generate_markdown_report(
    summary: Dict[str, Any], templates: List[Dict[str, Any]]
) -> str:
    lines: List[str] = []
    lines.append("# LLM Usage Analysis Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total requests: {summary.get('total', 0)}")
    lines.append(f"- Avg tokens in: {summary.get('avg_tokens_in', 0):.2f}")
    lines.append(f"- Avg tokens out: {summary.get('avg_tokens_out', 0):.2f}")
    lines.append(f"- Avg latency (ms): {summary.get('avg_latency_ms', 0):.2f}")
    lines.append("")
    lines.append("### Requests by model")
    for model, count in (
        summary.get("by_model", {}).most_common()
        if hasattr(summary.get("by_model", {}), "most_common")
        else summary.get("by_model", {}).items()
    ):
        lines.append(f"- {model or 'unknown'}: {count}")

    lines.append("")
    lines.append("## Top Tokens")
    for token, count in summary.get("top_tokens", [])[:20]:
        lines.append(f"- {token}: {count}")

    lines.append("")
    lines.append("## Top Bigrams")
    for phrase, count in summary.get("top_bigrams", [])[:20]:
        lines.append(f"- {phrase}: {count}")

    lines.append("")
    lines.append("## Prompt Templates")
    if not templates:
        lines.append("- No recurring templates detected (min support = 2)")
    for t in templates:
        lines.append(f"### Template ({t['occurrences']}x)")
        lines.append("")
        lines.append(f"``\n{t['template']}\n``")
        if t.get("slots"):
            lines.append(
                "- Slots: " + ", ".join(f"{k}={v}" for k, v in t["slots"].items())
            )
        if t.get("examples"):
            lines.append("- Examples:")
            for ex in t["examples"]:
                lines.append(f"  - {ex}")
        lines.append("")

    return "\n".join(lines)

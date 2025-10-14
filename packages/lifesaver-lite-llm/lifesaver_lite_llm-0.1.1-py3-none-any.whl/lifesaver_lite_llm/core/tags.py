from __future__ import annotations

from typing import Dict, List


def tag_flow(rec: Dict[str, object]) -> List[str]:
    """Heuristic tagging of a flow/row based on content.

    Accepts either legacy rows (input_text/output_text) or flow rows (req_body/resp_body).
    """
    input_text = rec.get("input_text") or rec.get("req_body") or ""
    output_text = rec.get("output_text") or rec.get("resp_body") or ""
    text = f"{input_text}\n{output_text}"
    t = str(text).lower()
    tags: List[str] = []
    try:
        if int(rec.get("tokens_out", 0) or 0) > 0:
            tags.append("generation")
    except Exception:
        pass
    if any(
        k in t
        for k in [
            "tool",
            "function",
            "call",
            "json_schema",
            "tool_call",
            "function_call",
        ]
    ):
        tags.append("tooling")
    if any(
        k in t
        for k in ["search", "retrieve", "retrieval", "kb", "knowledge base", "vector"]
    ):
        tags.append("retrieval")
    if any(k in t for k in ["image", "vision", "multimodal", "audio", "speech"]):
        tags.append("multimodal")
    # Few-shot / examples
    if any(
        k in t
        for k in ["q:", "a:", "input:", "output:", "example", "few-shot", "few shot"]
    ):
        tags.append("fewshot")
    # Formatting / structured
    if any(
        k in t
        for k in [
            "json",
            "schema",
            "fields:",
            "return valid json",
            "respond in json",
            "output as json",
        ]
    ):
        tags.append("formatting")
    # Safety / guardrails
    if any(
        k in t
        for k in [
            "guardrail",
            "policy",
            "red team",
            "refuse",
            "do not",
            "never provide",
        ]
    ):
        tags.append("safety")
    # Role prompting
    if any(t.strip().startswith(prefix) for prefix in ["you are", "system:"]):
        tags.append("role")
    # Reasoning hints
    if any(
        phrase in t
        for phrase in [
            "let's think step by step",
            "chain of thought",
            "reason step by step",
            "thought:",
        ]
    ):
        tags.append("reasoning")
    if not tags:
        tags.append("general")
    return tags

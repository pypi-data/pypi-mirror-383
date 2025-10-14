from __future__ import annotations

import re
from typing import Dict, List, Any

from .templates import normalize_prompt


# Define categories and technique patterns (heuristic)
TECHNIQUE_PATTERNS = {
    "reasoning": {
        "label": "Reasoning",
        "techniques": {
            "cot": [
                r"let'?s think step by step",
                r"chain[- ]?of[- ]?thought",
                r"reason step by step",
            ],
            "react": [
                r"\bthought:\b.*\baction:\b.*\bobservation:\b",
            ],
            "tree_of_thought": [r"tree[- ]of[- ]thought", r"branch(es)?"],
            "graph_of_thought": [r"graph[- ]of[- ]thought"],
            "self_consistency": [r"self[- ]?consisten(cy|t)", r"sample multiple"],
            "plan_and_solve": [r"plan\s+then\s+solve", r"first plan"],
            "program_of_thought": [
                r"program[- ]of[- ]thought",
                r"python|pseudo\s*code",
            ],
            "deliberate": [r"deliberate", r"multiple drafts|refine"],
        },
    },
    "fewshot": {
        "label": "Few-shot / Examples",
        "techniques": {
            "q_a_pairs": [r"\bQ:\b.*\bA:\b"],
            "input_output_pairs": [r"\bInput:\b.*\bOutput:\b"],
            "multiple_examples": [r"example\s*\d?\s*[:\-]"],
        },
    },
    "tooling": {
        "label": "Tool Use",
        "techniques": {
            "tool_calls": [r"\btool(s)?\b", r"function[_ -]?call", r"functions?\b"],
            "json_schema": [r"json\s*schema", r"parameters\s*:\s*\{"],
            "react_loop": [r"\bthought:\b", r"\baction:\b", r"\bobservation:\b"],
        },
    },
    "formatting": {
        "label": "Structured Output",
        "techniques": {
            "json_output": [
                r"output\s+as\s+json",
                r"return\s+valid\s+json",
                r"respond\s+in\s+json",
            ],
            "valid_schema": [r"match\s+this\s+schema", r"fields?:\s*\[?\w"],
        },
    },
    "retrieval": {
        "label": "Retrieval / RAG",
        "techniques": {
            "rag": [
                r"\brag\b",
                r"retriev(e|al)",
                r"knowledge\s*base",
                r"vector(s)?",
                r"embedding",
            ],
            "search": [r"\bsearch\b", r"web\s*search", r"browse(r|ing)"],
        },
    },
    "multiagent": {
        "label": "Multi-Agent Orchestration",
        "techniques": {
            "planner_critic_executor": [r"planner", r"critic", r"executor"],
            "delegation": [r"delegate", r"assign\s+to\s+agent"],
            "workflow": [
                r"workflow",
                r"state\s*machine",
                r"pipeline",
                r"orchestr(ate|ation)",
            ],
        },
    },
    "multimodal": {
        "label": "Multimodal",
        "techniques": {
            "vision": [r"image", r"vision", r"describe\s+image"],
            "audio": [r"audio", r"speech", r"transcrib(e|ing)", r"asr"],
        },
    },
    "safety": {
        "label": "Safety / Guardrails",
        "techniques": {
            "guardrails": [r"guardrail", r"policy", r"red\s*team"],
            "refusal": [r"do not .* output", r"never .* provide", r"refuse"],
        },
    },
    "role": {
        "label": "Role / System Prompting",
        "techniques": {
            "system_role": [r"^you are\b", r"^system:\b"],
        },
    },
}


def extract_prompting_techniques(
    prompts: List[str], min_support: int = 1
) -> Dict[str, Any]:
    compiled: Dict[str, Dict[str, List[re.Pattern[str]]]] = {}
    for cid, cat in TECHNIQUE_PATTERNS.items():
        compiled[cid] = {}
        for tid, pats in cat["techniques"].items():
            compiled[cid][tid] = [re.compile(p, re.I | re.S) for p in pats]

    # Normalize once
    norm_prompts = [normalize_prompt(p) for p in prompts if p and p.strip()]

    categories: Dict[str, Any] = {}
    for cid, cat in TECHNIQUE_PATTERNS.items():
        cat_label = cat["label"]
        techs_out = []
        for tid, regs in compiled[cid].items():
            matches: List[str] = []
            conf_total = 0
            for p in norm_prompts:
                hit_all = (
                    all(r.search(p) for r in regs)
                    if len(regs) > 1
                    else any(r.search(p) for r in regs)
                )
                if hit_all:
                    matches.append(p)
                    conf_total += sum(1 for r in regs if r.search(p))
            if len(matches) >= min_support:
                techs_out.append(
                    {
                        "id": tid,
                        "label": tid.replace("_", " ").title(),
                        "count": len(matches),
                        "examples": matches[:3],
                        "confidence": round(conf_total / max(1, len(matches)), 2),
                    }
                )
        # Sort techniques by count desc
        techs_out.sort(key=lambda t: (t["count"], t.get("confidence", 0)), reverse=True)
        if techs_out:
            categories[cid] = {
                "id": cid,
                "label": cat_label,
                "techniques": techs_out,
                "count": sum(t["count"] for t in techs_out),
            }

    # Also expose top normalized templates via grouping
    from collections import defaultdict

    groups: Dict[str, List[str]] = defaultdict(list)
    for p in norm_prompts:
        groups[p].append(p)
    templates = [
        {"template": k, "occurrences": len(v), "examples": v[:2]}
        for k, v in groups.items()
    ]
    templates.sort(key=lambda x: x["occurrences"], reverse=True)

    return {"categories": categories, "templates": templates}

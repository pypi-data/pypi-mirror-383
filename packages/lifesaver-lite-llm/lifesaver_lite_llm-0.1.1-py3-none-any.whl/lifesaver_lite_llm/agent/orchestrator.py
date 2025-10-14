from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


def load_providers_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class Provider:
    id: str
    match: str
    pricing_input_per_1k: float
    pricing_output_per_1k: float
    quality: float

    @classmethod
    def from_dict(cls, pid: str, d: Dict[str, Any]) -> "Provider":
        pr = d.get("pricing", {})
        return cls(
            id=pid,
            match=d.get("match", pid),
            pricing_input_per_1k=float(pr.get("input_per_1k", 0.0)),
            pricing_output_per_1k=float(pr.get("output_per_1k", 0.0)),
            quality=float(d.get("quality", 0.0)),
        )


class Orchestrator:
    def __init__(self, providers_config: Dict[str, Any]):
        self.providers: List[Provider] = [
            Provider.from_dict(pid, meta) for pid, meta in providers_config.items()
        ]
        self.providers.sort(key=lambda p: p.pricing_input_per_1k)

    def _select_provider(self, task: str, preferred: str = "auto") -> Provider:
        if preferred != "auto":
            for p in self.providers:
                if p.id == preferred:
                    return p
        # Heuristic: code tasks => highest quality; short/summarize => cheapest
        if re.search(r"code|debug|implement|refactor|unit test", task, re.I):
            return max(self.providers, key=lambda p: p.quality)
        if re.search(r"summari|short|quick|translate", task, re.I):
            return min(self.providers, key=lambda p: p.pricing_input_per_1k)
        # default: balanced score
        return max(
            self.providers,
            key=lambda p: (
                p.quality / (1e-9 + p.pricing_input_per_1k + p.pricing_output_per_1k)
            ),
        )

    def plan(self, task: str, preferred: str = "auto") -> Dict[str, Any]:
        provider = self._select_provider(task, preferred)
        steps = [
            "Clarify intent and constraints",
            "Identify inputs/outputs and edge cases",
            "Choose provider and prompt template",
            "Execute subtasks and validate results",
            "Assemble outputs and self-check",
        ]
        template = (
            "You are an expert agent. Task: {task}. "
            "Provide a minimal, testable plan and deliverables."
        )
        return {
            "provider": provider.id,
            "estimated_cost_per_1k": provider.pricing_input_per_1k
            + provider.pricing_output_per_1k,
            "quality": provider.quality,
            "template": template,
            "steps": steps,
        }

    def run(self, task: str, preferred: str = "auto") -> Dict[str, Any]:
        provider = self._select_provider(task, preferred)
        # Offline deterministic execution: echo a structured response
        plan = self.plan(task, preferred=provider.id)
        result = {
            "provider": provider.id,
            "plan_steps": plan["steps"],
            "output": self._offline_execute(task),
        }
        return result

    def _offline_execute(self, task: str) -> str:
        # Toy execution: if task suggests summarize, we return a checklist; if translate, a stub; else a plan
        if re.search(r"summari", task, re.I):
            return "Summary: Identify key points, evidence, and next actions."
        if re.search(r"translate", task, re.I):
            return "Translation stub: Provide bilingual glossary and sample lines."
        if re.search(r"test|unit", task, re.I):
            return "Testing plan: Arrange-Act-Assert, fixtures, and coverage targets."
        return (
            "Plan: Decompose into subtasks, define interfaces, implement, and validate."
        )

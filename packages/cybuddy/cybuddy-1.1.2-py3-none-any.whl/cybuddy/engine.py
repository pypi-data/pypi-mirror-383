from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class AnswerEngine(Protocol):
    def explain(self, text: str) -> str: ...
    def tip(self, text: str) -> str: ...
    def assist(self, text: str) -> str: ...
    def report(self, text: str) -> str: ...
    def quiz(self, text: str) -> str: ...
    def plan(self, text: str) -> str: ...


@dataclass(frozen=True)
class HeuristicEngine:
    explain_fn: callable
    tip_fn: callable
    assist_fn: callable
    report_fn: callable
    quiz_fn: callable
    plan_fn: callable

    def explain(self, text: str) -> str:
        return self.explain_fn(text)

    def tip(self, text: str) -> str:
        return self.tip_fn(text)

    def assist(self, text: str) -> str:
        return self.assist_fn(text)

    def report(self, text: str) -> str:
        return self.report_fn(text)

    def quiz(self, text: str) -> str:
        return self.quiz_fn(text)

    def plan(self, text: str) -> str:
        return self.plan_fn(text)



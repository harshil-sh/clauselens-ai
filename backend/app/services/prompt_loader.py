from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import Protocol


_PROMPT_TOKEN_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


class PromptTemplate(str, Enum):
    SUMMARY_V1 = "summary_v1"
    CLAUSE_EXTRACTION_V1 = "clause_extraction_v1"
    RISK_ASSESSMENT_V1 = "risk_assessment_v1"


class PromptLoader(Protocol):
    def load(self, template: PromptTemplate) -> str:
        ...

    def render(self, template: PromptTemplate, **context: str) -> str:
        ...


class PromptTemplateError(ValueError):
    pass


class FilePromptLoader:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parents[1] / "prompts"

    def load(self, template: PromptTemplate) -> str:
        path = self.base_dir / f"{template.value}.txt"
        try:
            return path.read_text(encoding="utf-8").strip()
        except FileNotFoundError as exc:
            raise PromptTemplateError(f"Prompt template not found: {template.value}") from exc

    def render(self, template: PromptTemplate, **context: str) -> str:
        prompt_text = self.load(template)
        missing_tokens = {
            token
            for token in _PROMPT_TOKEN_PATTERN.findall(prompt_text)
            if token not in context
        }
        if missing_tokens:
            missing = ", ".join(sorted(missing_tokens))
            raise PromptTemplateError(f"Missing prompt context values: {missing}")

        return _PROMPT_TOKEN_PATTERN.sub(
            lambda match: context[match.group(1)],
            prompt_text,
        )

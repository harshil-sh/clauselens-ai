from __future__ import annotations

import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field

from app.clients.interfaces import (
    ClauseContext,
    ClauseExtractionPayload,
    DocumentAnalysisAIClient,
    RiskAssessmentPayload,
    SummaryPayload,
)
from app.services.prompt_loader import PromptLoader, PromptTemplate


class SummaryResponseModel(BaseModel):
    document_type: str
    short_summary: str
    key_points: list[str] = Field(default_factory=list)


class ExtractedClauseResponseModel(BaseModel):
    heading: str
    category: str
    extracted_text: str
    confidence: float | None = None
    page_reference: int | None = None


class ClauseExtractionResponseModel(BaseModel):
    clauses: list[ExtractedClauseResponseModel] = Field(default_factory=list)


class RiskFlagResponseModel(BaseModel):
    severity: str
    title: str
    description: str
    recommendation: str
    impacted_clause_id: str | None = None


class RiskAssessmentResponseModel(BaseModel):
    risk_flags: list[RiskFlagResponseModel] = Field(default_factory=list)


class OpenAIDocumentAnalysisAIClient(DocumentAnalysisAIClient):
    def __init__(
        self,
        client: OpenAI,
        model: str,
        prompt_loader: PromptLoader,
    ) -> None:
        self._client = client
        self._model = model
        self._prompt_loader = prompt_loader

    def summarize(self, document_text: str) -> SummaryPayload:
        prompt = self._prompt_loader.render(
            PromptTemplate.SUMMARY_V1,
            document_text=document_text,
        )
        response = self._parse(prompt=prompt, response_model=SummaryResponseModel)
        return response.model_dump(mode="python")

    def extract_clauses(self, document_text: str) -> ClauseExtractionPayload:
        prompt = self._prompt_loader.render(
            PromptTemplate.CLAUSE_EXTRACTION_V1,
            document_text=document_text,
        )
        response = self._parse(prompt=prompt, response_model=ClauseExtractionResponseModel)
        return response.model_dump(mode="python")

    def assess_risks(
        self,
        document_text: str,
        clauses: list[ClauseContext],
    ) -> RiskAssessmentPayload:
        prompt = self._prompt_loader.render(
            PromptTemplate.RISK_ASSESSMENT_V1,
            document_text=document_text,
            clauses_json=json.dumps(clauses, indent=2),
        )
        response = self._parse(prompt=prompt, response_model=RiskAssessmentResponseModel)
        return response.model_dump(mode="python")

    def _parse(self, prompt: str, response_model: type[BaseModel]) -> BaseModel:
        completion = self._client.beta.chat.completions.parse(
            model=self._model,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_model,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ValueError("OpenAI did not return a parsed structured response.")
        return parsed


def build_openai_client(
    *,
    api_key: str,
    model: str,
    prompt_loader: PromptLoader,
) -> OpenAIDocumentAnalysisAIClient:
    return OpenAIDocumentAnalysisAIClient(
        client=OpenAI(api_key=api_key),
        model=model,
        prompt_loader=prompt_loader,
    )

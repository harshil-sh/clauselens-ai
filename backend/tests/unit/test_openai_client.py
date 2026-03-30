from types import SimpleNamespace

from app.clients.openai import OpenAIDocumentAnalysisAIClient, SummaryResponseModel
from app.services.prompt_loader import PromptLoader, PromptTemplate


class StubPromptLoader(PromptLoader):
    def load(self, template: PromptTemplate) -> str:
        return template.value

    def render(self, template: PromptTemplate, **context: str) -> str:
        return f"{template.value}:{context['document_text']}"


def test_openai_client_uses_typed_parse_call() -> None:
    captured: dict[str, object] = {}
    parsed_model = SummaryResponseModel(
        document_type="contract",
        short_summary="Short summary",
        key_points=["Point 1"],
    )

    def fake_parse(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(parsed=parsed_model),
                )
            ]
        )

    sdk_client = SimpleNamespace(
        beta=SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(parse=fake_parse),
            )
        )
    )
    client = OpenAIDocumentAnalysisAIClient(
        client=sdk_client,
        model="gpt-4.1-mini",
        prompt_loader=StubPromptLoader(),
    )

    payload = client.summarize("Service agreement text")

    assert payload["document_type"] == "contract"
    assert captured["model"] == "gpt-4.1-mini"
    assert captured["temperature"] == 0
    assert captured["response_format"] is SummaryResponseModel
    assert captured["messages"] == [
        {
            "role": "user",
            "content": "summary_v1:Service agreement text",
        }
    ]

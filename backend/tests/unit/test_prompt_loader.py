import pytest

from app.services.prompt_loader import FilePromptLoader, PromptTemplate, PromptTemplateError


def test_file_prompt_loader_reads_and_renders_prompt(tmp_path) -> None:
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "summary_v1.txt").write_text("Hello {{name}}", encoding="utf-8")

    loader = FilePromptLoader(base_dir=prompts_dir)

    assert loader.load(PromptTemplate.SUMMARY_V1) == "Hello {{name}}"
    assert loader.render(PromptTemplate.SUMMARY_V1, name="ClauseLens") == "Hello ClauseLens"


def test_file_prompt_loader_rejects_missing_context(tmp_path) -> None:
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "risk_assessment_v1.txt").write_text(
        "Missing {{document_text}} and {{clauses_json}}",
        encoding="utf-8",
    )

    loader = FilePromptLoader(base_dir=prompts_dir)

    with pytest.raises(PromptTemplateError, match="clauses_json, document_text"):
        loader.render(PromptTemplate.RISK_ASSESSMENT_V1)

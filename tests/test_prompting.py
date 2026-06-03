from pathlib import Path

from eoi_analyzer.prompting import PromptLibrary


def test_prompt_library_loads_builtin_prompt():
    prompt = PromptLibrary().render("recommendation_user.md", team_context="team", profile_json="{}", document_text="doc")

    assert "Skills & Staffing Needs" in prompt
    assert "Review Rubric Alignment" in prompt
    assert "team" in prompt
    assert "{}" in prompt
    assert "doc" in prompt


def test_prompt_library_loads_eoi_assessment_prompt():
    prompt = PromptLibrary().render("eoi_assessment_user.md", team_context="team", profile_json="{}", document_text="doc")

    assert "To what extent is the project scope well-defined?" in prompt
    assert "Do you recommend this project be paired with a VISS Center?" in prompt


def test_prompt_library_uses_override_directory(tmp_path: Path):
    override = tmp_path / "recommendation_user.md"
    override.write_text("Custom $value", encoding="utf-8")

    prompt = PromptLibrary(tmp_path).render("recommendation_user.md", value="prompt")

    assert prompt == "Custom prompt"

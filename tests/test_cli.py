import json
from pathlib import Path

from eoi_analyzer.cli import build_parser, write_analysis_outputs
from eoi_analyzer.config import DEFAULT_INPUT_DIR
from eoi_analyzer.results import BatchAnalysis, DocumentAnalysis


def test_cli_defaults_to_eois_and_generates_letters():
    args = build_parser().parse_args([])

    assert args.path is None
    assert DEFAULT_INPUT_DIR == "eois"
    assert args.skip_letter is False
    assert args.all_documents is False


def test_write_analysis_outputs_writes_profile_plan_recommendation_and_loi(tmp_path: Path):
    batch = BatchAnalysis(
        analyses=[
            DocumentAnalysis(
                source_path="/tmp/eois/example.pdf",
                source_name="Example EoI.pdf",
                text_char_count=123,
                engagement_snapshot="profile markdown",
                recommendation="recommendation markdown",
                project_plan="project plan markdown",
                letter_of_intent="loi markdown",
                engagement_profile={"title": "Example"},
                agent_review="agent review markdown",
            )
        ]
    )

    write_analysis_outputs(batch, tmp_path)

    expected_files = {
        "Example-EoI_engagement_profile.json",
        "Example-EoI_engagement_profile.md",
        "Example-EoI_recommendation.md",
        "Example-EoI_project_plan.md",
        "Example-EoI_letter_of_intent.md",
        "manifest.json",
    }
    assert {path.name for path in tmp_path.iterdir()} == expected_files

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["analyses"][0]["source_name"] == "Example EoI.pdf"
    assert manifest["analyses"][0]["engagement_profile"]["title"] == "Example"

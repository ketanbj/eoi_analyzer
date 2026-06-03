import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

from .analyzer import EOIAnalyzer
from .config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR
from .results import BatchAnalysis, DocumentAnalysis


def slugify_filename(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return slug or "document"


def reserve_slug(base: str, used_slugs: Dict[str, int]) -> str:
    count = used_slugs.get(base, 0) + 1
    used_slugs[base] = count
    if count == 1:
        return base
    return f"{base}-{count}"


def write_markdown_file(path: Path, title: str, analysis: DocumentAnalysis, body: str) -> None:
    path.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"Source: `{analysis.source_path}`",
                f"Extracted characters: `{analysis.text_char_count}`",
                "",
                body,
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_analysis_outputs(batch: BatchAnalysis, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    used_slugs: Dict[str, int] = {}

    for analysis in batch.analyses:
        stem = slugify_filename(Path(analysis.source_name).stem)
        slug = reserve_slug(stem, used_slugs)

        write_markdown_file(
            output_dir / f"{slug}_recommendation.md",
            f"Recommendation: {analysis.source_name}",
            analysis,
            analysis.recommendation,
        )
        if analysis.agent_review:
            write_markdown_file(
                output_dir / f"{slug}_engagement_profile.md",
                f"Engagement Profile: {analysis.source_name}",
                analysis,
                analysis.agent_review,
            )
        if analysis.engagement_profile:
            (output_dir / f"{slug}_engagement_profile.json").write_text(
                json.dumps(analysis.engagement_profile, indent=2),
                encoding="utf-8",
            )
        write_markdown_file(
            output_dir / f"{slug}_project_plan.md",
            f"Project Plan: {analysis.source_name}",
            analysis,
            analysis.project_plan,
        )

        if analysis.letter_of_intent:
            write_markdown_file(
                output_dir / f"{slug}_letter_of_intent.md",
                f"Letter of Intent: {analysis.source_name}",
                analysis,
                analysis.letter_of_intent,
            )

    (output_dir / "manifest.json").write_text(
        json.dumps(batch.to_dict(), indent=2),
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate software engineering recommendations, project plans, and LoI drafts from one document "
            "or every PDF in the default EoI folder."
        )
    )
    parser.add_argument(
        "path",
        nargs="?",
        help=f"Path to a document or folder. Defaults to the local EoI folder: {DEFAULT_INPUT_DIR}",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Folder where generated files will be written. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--include-letter",
        action="store_true",
        help="Generate Letter of Intent drafts. This is already enabled by default.",
    )
    parser.add_argument(
        "--skip-letter",
        action="store_true",
        help="Skip Letter of Intent draft generation.",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="When PATH is a folder, only process files directly inside that folder.",
    )
    parser.add_argument(
        "--team-context",
        help=(
            "Optional JSON file with private team capabilities, past projects, or funding notes "
            "to merge with the default GT CSSE/VISS context."
        ),
    )
    parser.add_argument(
        "--prompt-dir",
        help=(
            "Optional folder of prompt template overrides. Files with the same names as "
            "eoi_analyzer/prompts/*.md will replace the built-in prompts."
        ),
    )
    parser.add_argument(
        "--all-documents",
        action="store_true",
        help="When PATH is a folder, process all supported document types instead of PDFs only.",
    )
    return parser


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required. Set it in your environment or .env file.")

    source_path = Path(args.path or DEFAULT_INPUT_DIR)
    output_dir = Path(args.output_dir)
    analyzer = EOIAnalyzer(api_key, team_context_path=args.team_context, prompt_dir=args.prompt_dir)
    include_letter = not args.skip_letter
    extensions = None if args.all_documents else {".pdf"}

    if source_path.is_dir():
        document_scope = "all supported documents" if args.all_documents else "PDFs"
        print(f"Analyzing {document_scope} in {source_path}...")
        batch = analyzer.analyze_folder(
            source_path,
            recursive=not args.non_recursive,
            include_letter=include_letter,
            extensions=extensions,
        )
    else:
        print(f"Analyzing document {source_path}...")
        batch = BatchAnalysis(
            analyses=[
                analyzer.analyze_document(source_path, include_letter=include_letter)
            ]
        )

    write_analysis_outputs(batch, output_dir)

    print(f"Wrote {len(batch.analyses)} document analysis result(s) to {output_dir}.")
    if batch.failures:
        print(f"{len(batch.failures)} document(s) failed. See manifest.json for details.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

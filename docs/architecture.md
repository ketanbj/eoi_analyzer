# Architecture

## Overview

EOI Analyzer is organized around a bounded agent pipeline. The pipeline converts raw document text into a structured engagement profile, enriches it with deterministic checks, runs rubric and scientific-outcome assessments, then generates the final recommendation, project plan, and LoI.

High-level flow:

```text
document files
  -> text extraction
  -> engagement profile intake
  -> capability matching
  -> collaboration risk analysis
  -> scientific outcome and follow-on assessment
  -> VISS-style EOI rubric assessment
  -> optional past-project matching
  -> weighted scorecard
  -> review findings
  -> recommendation, project plan, and LoI generation
  -> markdown/json outputs
```

## Module Map

- `app.py`: Flask upload UI.
- `eoi_analyzer/cli.py`: command-line batch workflow and output writer.
- `eoi_analyzer/analyzer.py`: orchestration layer and model-call helper.
- `eoi_analyzer/agents.py`: agent implementations and deterministic enrichers.
- `eoi_analyzer/profile.py`: dataclasses for structured engagement profiles and rubric assessment.
- `eoi_analyzer/results.py`: batch and per-document result dataclasses.
- `eoi_analyzer/utils.py`: document text extraction and folder traversal.
- `eoi_analyzer/knowledge.py`: default GT VISS/CSSE capability model and optional private-context merge.
- `eoi_analyzer/prompting.py`: prompt-template loading and rendering.
- `eoi_analyzer/prompts/`: editable Markdown prompt templates.
- `tests/`: unit tests.
- `.github/workflows/tests.yml`: pull-request and main-branch CI.

## Orchestration

`EOIAnalyzer.analyze_document()` is the main single-document entry point:

1. Extract text with `extract_text_from_document()`.
2. Build an `EngagementProfile` through `build_engagement_profile()`.
3. Render the profile summary.
4. Generate a recommendation.
5. Generate a project plan.
6. Optionally generate a Letter of Intent.
7. Return a `DocumentAnalysis`.

`EOIAnalyzer.analyze_folder()` iterates documents with `iter_document_paths()`, runs `analyze_document()` for each file, and records failures as `DocumentFailure` objects.

## Agent Pipeline

The pipeline is intentionally split into smaller stages instead of one large prompt:

- `DocumentIntakeAgent`: model-generated structured extraction from the source document.
- `CapabilityMatcherAgent`: deterministic keyword matching against GT VISS/CSSE engagement modes and skill profiles.
- `CollaborationRiskAgent`: deterministic checks for PI ownership, multi-PI coordination, locations, time-zone overlap, prior relationship, deadlines, and data-governance concerns.
- `ScientificOutcomeAgent`: model-generated assessment of likely scientific outcomes and follow-on opportunities.
- `EOIAssessmentAgent`: model-generated VISS-style rubric assessment with deterministic fallback.
- `PastProjectMatcherAgent`: deterministic matching against optional local `past_projects`.
- `ScorecardAgent`: weighted scoring and recommendation decision.
- `ProfileReviewAgent`: deterministic review findings for missing or thin evidence.

This structure keeps the model focused on interpretation and synthesis while preserving deterministic behavior for repeatable checks.

## Data Model

The central object is `EngagementProfile`. It contains:

- source metadata and title
- PI team, institutions, locations, and time zones
- scientific and software objectives
- existing assets, constraints, data considerations, deadlines, and open questions
- evidence items
- capability matches
- collaboration risks
- scientific outcomes
- follow-on opportunities
- past-project matches
- VISS rubric assessment
- scorecard
- recommendation decision
- review findings

`EOIAssessment` mirrors the VISS-style assessment rubric: scope, technical components, feasibility, SWE impact, scientific-field impact, readiness, project types, engagement models, pairing recommendation, comments, and critical questions.

## Prompt System

Prompt templates live in `eoi_analyzer/prompts/`. `PromptLibrary` loads built-in templates by default and can override them from:

- `--prompt-dir`
- `EOI_ANALYZER_PROMPT_DIR`

Templates use `$placeholder` variables through `string.Template.safe_substitute`.

## Team Context

`knowledge.py` provides a default GT VISS/CSSE context with:

- mission
- engagement modes
- skill profiles
- broader skill areas
- skill acquisition channels
- funding opportunity categories
- optional past projects

`load_team_context()` merges this default with a local JSON file passed through `--team-context` or `EOI_ANALYZER_TEAM_CONTEXT`.

## Deterministic Versus Model-Generated Behavior

Model-generated:

- initial structured intake
- scientific outcomes and follow-on opportunities
- VISS rubric assessment
- final recommendation narrative
- project plan narrative
- Letter of Intent narrative

Deterministic:

- file discovery and extension filtering
- text extraction dispatch
- capability keyword matching
- collaboration risk checks
- time-zone overlap estimates
- past-project term matching
- scorecard weighting
- fallback assessments
- output-file writing

## Error Handling

Document extraction errors are raised from `utils.py`. During folder analysis, exceptions are captured per file and written to `BatchAnalysis.failures` so a single bad document does not stop the entire run.

When a model-backed agent fails to return valid JSON, the agent creates a conservative fallback profile or assessment and adds open questions or review findings.

## Extension Points

Likely extension points:

- Add new document extractors in `utils.py`.
- Add more VISS-specific fields to `EOIAssessment`.
- Add richer skill availability or staff capacity in `knowledge.py` and team-context JSON.
- Add portfolio-level stack ranking over `manifest.json`.
- Add reviewer-editable rubric forms before final recommendation, project plan, and LoI generation.
- Add export formats such as CSV, HTML, or review-session packets.
- Replace keyword matching with embeddings for past-project and capability matching.


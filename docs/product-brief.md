# Product Brief

## Purpose

EOI Analyzer helps GT VISS/CSSE review Expression of Interest documents and produce consistent downstream material:

- An agentic engagement profile with project facts, risks, capabilities, scorecard, and VISS-style rubric assessment.
- A software engineering recommendation.
- A practical project plan.
- A Letter of Intent draft.

The goal is to reduce reviewer busywork, make assumptions visible, and improve consistency across multiple EOIs. The tool should support human review sessions, not replace them.

## Primary Users

- VISS and CSSE reviewers screening incoming EOIs.
- RSEs and engineering leads preparing project recommendations.
- Program or product leads comparing scope, feasibility, staffing needs, and follow-on opportunities.
- Review coordinators who need repeatable outputs for many PDFs in a folder.

## Inputs

The analyzer accepts:

- PDF files, including the default batch mode for every PDF in `eois/`.
- `.docx`, `.txt`, `.md`, and `.markdown` files when explicitly requested or uploaded through the Flask app.
- Optional local team-context JSON with private capabilities, past projects, staffing availability, and reusable lessons.
- Optional prompt-template overrides.

## Outputs

For each source document, the CLI writes:

- `<slug>_engagement_profile.md`
- `<slug>_engagement_profile.json`
- `<slug>_recommendation.md`
- `<slug>_project_plan.md`
- `<slug>_letter_of_intent.md`, unless `--skip-letter` is used
- `manifest.json` with all analyses and per-document failures

The Flask app renders the same analysis results in the browser after document upload.

## Product Principles

- Evidence first: extracted claims should be grounded in the source document when possible.
- Rubric aligned: the review profile should loosely follow the VISS EOI assessment questions.
- Human review friendly: outputs should surface open questions, assumptions, and risks clearly.
- Batch native: folder processing should be the normal path for review rounds.
- Prompt editable: reviewers should be able to tune language and review emphasis without changing Python code.
- Team aware: recommendations should consider GT VISS/CSSE capabilities, staffing routes, past projects, time zones, PI coordination, and follow-on proposal potential.

## Non-Goals

- The tool does not randomly assign EOIs to centers.
- The tool does not run the official final stack-ranking process.
- The tool does not make binding funding or pairing decisions.
- The tool does not verify every factual claim outside the source document.
- The tool does not replace PI follow-up conversations.

## Success Criteria

The product is working well when reviewers can:

- Process a folder of EOIs with one command.
- See consistent rubric-oriented summaries across all projects.
- Identify unclear scope, feasibility risks, missing PI information, timeline gaps, and data-governance issues quickly.
- Compare project fit against GT VISS/CSSE capabilities and prior work.
- Move from EOI review to a draft recommendation, project plan, and LoI with less manual formatting.

## Current Maturity

The implementation is a practical first version. It has a bounded agent pipeline, tests, CI, prompt overrides, team-context overrides, and batch output. The highest-value next improvements are likely:

- Reviewer calibration against historical EOI decisions.
- Better structured export for stack ranking.
- Richer private team-context data, especially staffing availability and past project outcomes.
- A review UI for editing rubric answers before generating final LoI text.
- Cross-EOI comparison and portfolio-level ranking.


# Documentation

This folder contains the longer-form documentation for the EOI Analyzer. The root `README.md` is the quick start; these documents explain the product intent, operating model, architecture, and review-process fit.

## Documents

- [Product Brief](product-brief.md): product goal, users, outputs, success criteria, and non-goals.
- [Usage Guide](usage.md): setup, CLI usage, Flask usage, output files, environment variables, prompt overrides, and team-context files.
- [Architecture](architecture.md): module map, agent pipeline, data model, deterministic versus model-generated behavior, and extension points.
- [VISS Process Mapping](viss-process-mapping.md): how the implementation maps to the EOI assessment rubric and which process steps remain human-led.
- [Prompts and Team Context](prompts-and-team-context.md): how to edit prompt templates and encode GT VISS/CSSE capabilities, past projects, staffing options, and reusable lessons.
- [Testing and CI](testing-and-ci.md): local test commands, GitHub Actions behavior, and guidance for adding coverage.

## Current Product Shape

EOI Analyzer is a decision-support tool for turning EOI documents into structured review material, software engineering recommendations, project plans, and Letter of Intent drafts. It is not intended to replace VISS center review, stack ranking, PI follow-up, or final project selection.


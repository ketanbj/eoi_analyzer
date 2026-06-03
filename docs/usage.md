# Usage Guide

## Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file or export the required API key:

```bash
echo 'OPENAI_API_KEY="your-openai-api-key"' > .env
```

The analyzer uses `OPENAI_MODEL` and `LITELLM_PROXY_URL` from the environment when set. Defaults are defined in `eoi_analyzer/config.py`.

## CLI: Default EOI Folder

Run the default batch workflow:

```bash
uv run eoi-analyzer
```

This processes every PDF under `eois/`, generates engagement profiles, recommendations, project plans, and Letter of Intent drafts, and writes output files to `outputs/`.

## CLI: Different Folder

```bash
uv run eoi-analyzer path/to/eoi_docs --output-dir outputs
```

Folder inputs are recursive by default and include PDFs only unless `--all-documents` is provided.

## CLI: One Document

```bash
uv run eoi-analyzer path/to/document.pdf --output-dir outputs
```

Supported document types are `.pdf`, `.docx`, `.txt`, `.md`, and `.markdown`.

## CLI Options

```bash
uv run eoi-analyzer --help
```

Important options:

- `--output-dir`: output folder, default `outputs/`.
- `--skip-letter`: skip Letter of Intent generation.
- `--non-recursive`: only process direct children of the input folder.
- `--all-documents`: include all supported document types when processing a folder.
- `--team-context`: load private team capabilities, past projects, staffing notes, and reusable lessons from JSON.
- `--prompt-dir`: use Markdown prompt overrides from a local folder.

## Output Files

For each source document, the CLI writes:

- Engagement profile Markdown for human review.
- Engagement profile JSON for downstream processing.
- Recommendation Markdown.
- Project plan Markdown.
- Letter of Intent Markdown unless skipped.

The CLI also writes `manifest.json`, which includes all successful analyses and any per-document failures.

## Flask App

Start the web app:

```bash
uv run python app.py
```

Open `http://127.0.0.1:5000`, upload one or more supported documents, and generate recommendations and plans. The web app includes Letter of Intent drafts by default.

## Prompt Overrides

Copy the built-in prompt files and edit them locally:

```bash
mkdir -p local_prompts
cp eoi_analyzer/prompts/*.md local_prompts/
uv run eoi-analyzer --prompt-dir local_prompts
```

The analyzer replaces built-in prompts only when a file with the same name exists in the override folder.

You can also set:

```bash
export EOI_ANALYZER_PROMPT_DIR=local_prompts
```

## Team Context

Use `--team-context` to add private knowledge without editing code:

```bash
uv run eoi-analyzer eois --team-context team_context.json
```

Example:

```json
{
  "past_projects": [
    {
      "name": "Example microscopy pipeline",
      "domain": "bioimaging",
      "technologies": ["Python", "workflow automation", "cloud storage"],
      "outcomes": ["reproducible image analysis", "publication support"],
      "lessons": [
        "Confirm data access before sprint planning",
        "Define acceptance tests with the PI"
      ]
    }
  ],
  "staffing_notes": [
    "RSE capacity is strongest for Python, data pipelines, and CI/CD in the next review cycle."
  ]
}
```

The default context is merged with the provided JSON file. Top-level keys in the JSON override or add to the default context.

## Operational Notes

- Batch runs may call the model multiple times per document. Use a small folder for prompt experiments.
- `outputs/` is ignored by git.
- Unsupported or unreadable documents are recorded in `manifest.json` as failures instead of stopping the whole batch.
- The analyzer should be treated as a drafting and review-support tool. Final pairing decisions, stack ranking, and applicant follow-up remain human-led.


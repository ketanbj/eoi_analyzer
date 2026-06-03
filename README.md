# eoi_analyzer
Generate software engineering recommendations, project plans, and Letter of Intent (LoI) drafts from Expression of Interest (EoI) and planning documents using OpenAI.

**input**: One or more `.pdf`, `.docx`, `.txt`, `.md`, or `.markdown` documents.

**output**:
- Agentic engagement profile highlighting scientific objectives, stakeholders, assets, constraints, GT VISS/CSSE capability fit, collaboration risks, scientific outcomes, and follow-on opportunities
- Software engineering recommendation with engagement type, workstreams, dependencies, risks, and clarifying questions
- Project plan with phases, milestones, deliverables, collaboration model, success measures, and risk register
- Optional LoI-ready narrative covering objectives, phased 3–6 month plan, deliverables, collaboration model, risks, and next steps

## analysis pipeline
The analyzer uses a bounded agentic workflow rather than one large prompt:

1. Extract a structured engagement profile from the source document.
2. Match the project to GT CSSE/VISS engagement modes and skill profiles.
3. Assess collaboration risks such as PI count, locations, time-zone overlap, deadlines, data access, and prior working relationships.
4. Evaluate scientific outcomes and realistic follow-on proposal or funding pathways.
5. Complete a VISS-style EOI review rubric covering scope, technical components, feasibility, SWE impact, scientific impact, readiness, project category, engagement model, center-pairing recommendation, comments, and critical follow-up questions.
6. Match against optional local past-project context.
7. Score the engagement and generate review findings.
8. Draft the recommendation, project plan, and optional Letter of Intent from the reviewed profile.

## usage (with [uv](https://github.com/astral-sh/uv))
1. Clone this repo and `cd` into it.
2. Create a `.env` file that includes your OpenAI API key (used by LiteLLM when proxying requests):
   ```bash
   echo 'OPENAI_API_KEY="your-openai-api-key"' > .env
   ```
   The app loads environment variables automatically with `python-dotenv` and routes all model calls through the LiteLLM proxy at `https://litellm-dev.pace.gatech.edu:4000/`.
3. Install the project dependencies with uv:
   ```bash
   uv sync
   ```
4. Launch the Flask app inside the synced environment:
   ```bash
   uv run python app.py
   ```

Navigate to http://127.0.0.1:5000, upload one or more documents, and press **Generate Recommendations and Plans**.

## folder processing
Use the CLI when the documents already live in the local `eois/` folder:

```bash
uv run eoi-analyzer
```

By default, this processes every PDF in `eois/`, generates engagement profiles, recommendations, project plans, and LoI drafts, and writes the outputs to `outputs/`.

To point at a different folder:

```bash
uv run eoi-analyzer path/to/eoi_docs --output-dir outputs
```

The CLI writes one engagement-profile markdown file, one engagement-profile JSON file, one recommendation markdown file, and one project-plan markdown file per source document, plus `manifest.json` with all generated outputs and per-document failures.

To skip LoI drafts:

```bash
uv run eoi-analyzer path/to/eoi_docs --output-dir outputs --skip-letter
```

By default, folders are processed recursively and only PDFs are included. Use `--all-documents` to include all supported document types, and use `--non-recursive` to process only files directly inside the given folder.

## team context
By default, the analyzer uses the public GT CSSE/VISS capability model. To include private team capabilities, prior engagements, or reusable lessons, pass a local JSON file:

```bash
uv run eoi-analyzer path/to/eoi_docs --team-context team_context.json
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
      "lessons": ["Confirm data access before sprint planning", "Define acceptance tests with the PI"]
    }
  ]
}
```

## prompt templates
Prompts live in `eoi_analyzer/prompts/` as editable Markdown templates. They use `$placeholder` variables such as `$team_context`, `$profile_json`, `$document_text`, `$recommendation`, and `$project_plan`.

To experiment without editing Python code, copy the prompt files into a local folder and point the CLI at it:

```bash
mkdir -p local_prompts
cp eoi_analyzer/prompts/*.md local_prompts/
uv run eoi-analyzer --prompt-dir local_prompts
```

You can also set:

```bash
export EOI_ANALYZER_PROMPT_DIR=local_prompts
```

The recommendation, project-plan, and LoI prompts ask the model to consider broad skill needs, including research software engineering, architecture, data engineering, AI/ML, MLOps, HPC/performance, cloud/infrastructure, security/privacy, UI/UX, testing, documentation, open-source governance, community support, training, product/program management, proposal development, and domain-science liaison work.

When proposing how to obtain skills, the prompts steer the model to consider GT CSSE/VISS staff, PI-team expertise, students or trainees, internal GT partners, external collaborators, reusable prior-project assets, open-source communities, vendor/cloud support, workshops or mentoring, and future proposal-funded hires or contracts.

## tests
Run the unit test suite locally with:

```bash
python -m pip install -e ".[test]"
python -m pytest
```

GitHub Actions runs the same tests on pull requests.

## documentation

Longer-form project documentation lives in [`docs/`](docs/):

- Product brief and product boundaries
- Usage guide for CLI, Flask, prompt overrides, and team context
- Architecture and agent pipeline details
- VISS process mapping
- Prompt and team-context customization guidance
- Testing and CI notes

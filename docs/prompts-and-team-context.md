# Prompts and Team Context

## Why Prompts Are Separate

The prompts live in Markdown files so reviewers can tune the analyzer without changing Python code. This is useful for:

- adjusting tone and structure of recommendations
- changing rubric emphasis
- adding review-session instructions
- tightening LoI style
- experimenting with different definitions of readiness, feasibility, or impact

## Built-In Prompt Files

The built-in prompt templates are in `eoi_analyzer/prompts/`:

- `document_intake_system.md`
- `document_intake_user.md`
- `scientific_outcome_system.md`
- `scientific_outcome_user.md`
- `eoi_assessment_system.md`
- `eoi_assessment_user.md`
- `engagement_snapshot_system.md`
- `engagement_snapshot_user.md`
- `recommendation_system.md`
- `recommendation_user.md`
- `project_plan_system.md`
- `project_plan_user.md`
- `letter_of_intent_system.md`
- `letter_of_intent_user.md`

## Prompt Overrides

Create a local prompt directory:

```bash
mkdir -p local_prompts
cp eoi_analyzer/prompts/*.md local_prompts/
```

Run with overrides:

```bash
uv run eoi-analyzer eois --prompt-dir local_prompts
```

Only files present in the override directory replace built-in templates. Missing files fall back to the built-in versions.

## Template Variables

Prompt templates use `$placeholder` variables. Common variables include:

- `$team_context`
- `$source_name`
- `$document_text`
- `$profile_json`
- `$recommendation`
- `$project_plan`
- `$today`

The template renderer uses safe substitution, so normal JSON braces can appear in prompt files.

## Prompt Editing Guidelines

When editing prompts:

- Keep JSON-output prompts strict about returning a single JSON object.
- Ask the model to distinguish source evidence from assumptions.
- Preserve fields expected by the dataclasses in `profile.py`.
- Keep the VISS rubric answer options exact when possible.
- Ask for concise critical questions rather than broad speculation.
- Include staffing and skill-sourcing instructions in recommendation, project-plan, and LoI prompts.
- Test prompt changes on one or two EOIs before running the full folder.

## Team Context

`knowledge.py` defines the default GT VISS/CSSE context:

- mission
- engagement modes
- skill profiles
- broader skill areas
- skill acquisition channels
- funding opportunity categories
- public source links
- empty `past_projects`

Use a local JSON file to add private information:

```bash
uv run eoi-analyzer eois --team-context team_context.json
```

The local context is merged with the default context.

## Useful Team-Context Fields

The analyzer can use any JSON fields in prompts, but the current code directly uses these fields:

- `name`
- `home_time_zone`
- `mission`
- `engagement_modes`
- `skill_profiles`
- `broader_skill_areas`
- `skill_acquisition_channels`
- `funding_opportunity_categories`
- `past_projects`

Fields that are useful for prompt-only context:

- `staffing_notes`
- `current_capacity`
- `preferred_engagement_constraints`
- `proposal_calendar`
- `known_center_strengths`
- `reviewer_preferences`
- `data_governance_requirements`

## Past Projects

Add `past_projects` to improve reuse recommendations:

```json
{
  "past_projects": [
    {
      "name": "Climate pipeline modernization",
      "domain": "climate modeling",
      "summary": "Refactored a research workflow into a tested, reproducible pipeline.",
      "technologies": ["Python", "workflow automation", "HPC", "CI/CD"],
      "outcomes": ["faster model runs", "reproducible datasets"],
      "lessons": [
        "Start with data provenance before optimizing performance",
        "Define acceptance tests with scientists before refactoring"
      ]
    }
  ]
}
```

`PastProjectMatcherAgent` currently uses simple term overlap. This is intentionally conservative and easy to test. A future version could use embeddings or reviewer-curated tags.

## Skill Modeling

The prompts and default context ask the analyzer to think beyond a narrow RSE assignment. Relevant skill areas include:

- research software engineering
- software architecture
- data engineering
- AI/ML engineering
- MLOps
- HPC and performance engineering
- cloud and infrastructure engineering
- security and privacy review
- UI/UX and visualization
- testing and quality assurance
- technical writing and documentation
- open-source governance
- community management
- training and curriculum development
- product management
- program management
- proposal development
- domain-science liaison

Skill sourcing channels include:

- GT CSSE/VISS staff
- PI-team domain expertise
- students, trainees, or fellows
- internal Georgia Tech partners
- external scientific collaborators
- reusable assets from past projects
- open-source community packages or maintainers
- vendor or cloud-provider support
- targeted workshops or mentoring
- future proposal-funded hires or contracts

## Safety And Review

Prompts should avoid presenting speculative claims as facts. For review use, prefer language like:

- "The EOI states..."
- "The profile suggests..."
- "This appears to require confirmation..."
- "A reviewer should ask..."

The final recommendation, project plan, and LoI should be treated as drafts until a human reviewer resolves high-severity findings and critical questions.


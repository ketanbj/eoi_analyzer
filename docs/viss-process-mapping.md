# VISS Process Mapping

## Process Fit

The current implementation loosely follows the EOI assessment process by generating a structured, rubric-oriented review for each EOI and using that review to inform the recommendation, project plan, and LoI.

The tool supports these process steps:

- Reading many EOIs from a folder.
- Producing consistent per-EOI assessments.
- Capturing scope, feasibility, impact, readiness, engagement model, pairing recommendation, and follow-up questions.
- Producing artifacts that can support review meetings and later applicant follow-up.

The tool does not automate these process steps:

- Randomly selecting two centers to assess each EOI.
- Combining independent center assessments.
- Deciding whether an EOI is acceptable for full review.
- Distributing final EOI collections to all centers.
- Running the official stack-ranking process.
- Making final pairing or funding decisions.

Those steps should remain human-led unless the governance workflow is explicitly added.

## Rubric Mapping

| Process question | Current implementation |
| --- | --- |
| 1. Scope definition rating | `EOIAssessment.scope_rating` |
| 2. Project summary and design approach | `scope_summary` and `design_approach_assessment` |
| 3. Technical components | `technical_components`; deterministic fallback infers categories from profile text |
| 4. Technical feasibility in 3-9 months | `technical_feasibility_rating` and scorecard feasibility |
| 5. Feasibility comments | `technical_feasibility_comment` |
| 6. SWE work addresses project goals | `swe_goal_impact_rating` and engineering leverage score |
| 7. Impact to scientific field | `scientific_field_impact_rating` and scientific impact score |
| 8. Impact comments | `impact_comment` |
| 9. Development readiness | `development_readiness`, collaboration risks, and review findings |
| 10. Project type | `project_types` |
| 11. Engagement model | `engagement_models` plus GT VISS/CSSE capability matching |
| 12. Engagement model rationale | `engagement_model_rationale` |
| 13. Recommend pairing with VISS Center | `viss_pairing_recommendation`; also constrains final recommendation decision |
| 14. General comments | `general_comments` and profile review findings |
| 15. Critical clarification questions | `critical_questions` and `open_questions` |

## Output Mapping

The generated engagement profile is the primary review artifact. It includes:

- PI team and locations.
- Scientific objectives.
- Software objectives.
- Assets, constraints, deadlines, and data considerations.
- GT VISS/CSSE capability fit.
- Collaboration risks.
- Scientific outcomes.
- Follow-on opportunities.
- VISS rubric assessment.
- Scorecard.
- Agent review findings.

The recommendation and project plan use this profile as grounding material. The LoI uses the profile, recommendation, and project plan.

## Review Decision Mapping

The VISS pairing recommendation uses the rubric options:

- `No`
- `Yes, pending on responses to follow-up questions`
- `Yes`

The analyzer's broader recommendation decision uses:

- `Proceed`
- `Proceed with conditions`
- `Discovery first`
- `Defer until clarified`

The `ScorecardAgent` applies the pairing recommendation as a constraint. For example, a rubric pairing recommendation of `No` forces the broader decision to `Defer until clarified`.

## Assessment Criteria Added Beyond The Rubric

The current implementation intentionally adds a few decision-support checks that are not explicit in the rubric:

- PI count and decision ownership.
- PI and collaborator locations.
- Estimated time-zone overlap with Atlanta.
- Prior working relationship with GT VISS/CSSE or the project team.
- Data access, governance, privacy, licensing, compute, and storage concerns.
- Fit to GT VISS/CSSE engagement modes and skill profiles.
- Skill needs and possible sourcing channels.
- Follow-on proposal, platform, sustainability, fellowship, or partnership opportunities.
- Reuse potential from prior projects in local team context.

These additions help reviewers move from "is this EOI acceptable?" to "what engagement could we actually run, staff, and hand off?"

## Recommended Human Workflow

1. Run the CLI across the EOI folder.
2. Review `manifest.json` for extraction failures.
3. Read each engagement profile before the recommendation, project plan, or LoI.
4. Confirm any high-severity findings and critical questions.
5. Calibrate the model-generated rubric answers against human reviewer judgment.
6. Use the recommendation and project plan as drafts for discussion, not final commitments.
7. Edit or regenerate the LoI only after the review team accepts scope, feasibility, staffing, and applicant follow-up questions.

## Future Process Enhancements

Potential enhancements if the repo should cover more of the VISS workflow:

- Add center-assignment metadata and support two independent assessments per EOI.
- Add reviewer identity, review status, and adjudication fields.
- Generate a cross-EOI stack-ranking table from `manifest.json`.
- Add a calibration set of previous EOIs and known decisions.
- Add an editing UI for rubric answers before narrative generation.
- Export review packets for full-center distribution.


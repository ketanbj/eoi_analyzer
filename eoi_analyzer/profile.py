from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


def _string_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _mapping_list(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


@dataclass
class EvidenceItem:
    claim: str
    source: str
    quote: str = ""
    confidence: str = "medium"

    @classmethod
    def from_dict(cls, payload: Dict[str, Any], default_source: str) -> "EvidenceItem":
        return cls(
            claim=str(payload.get("claim", "")).strip(),
            source=str(payload.get("source") or default_source).strip(),
            quote=str(payload.get("quote", "")).strip(),
            confidence=str(payload.get("confidence", "medium")).strip() or "medium",
        )


@dataclass
class Investigator:
    name: str
    role: str = ""
    institution: str = ""
    location: str = ""
    time_zone: str = ""
    evidence: str = ""

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Investigator":
        return cls(
            name=str(payload.get("name", "")).strip(),
            role=str(payload.get("role", "")).strip(),
            institution=str(payload.get("institution", "")).strip(),
            location=str(payload.get("location", "")).strip(),
            time_zone=str(payload.get("time_zone", "")).strip(),
            evidence=str(payload.get("evidence", "")).strip(),
        )


@dataclass
class CapabilityMatch:
    name: str
    category: str
    score: int
    rationale: str
    source: str = "GT CSSE public capability model"


@dataclass
class CollaborationRisk:
    name: str
    severity: str
    rationale: str
    mitigation: str


@dataclass
class ScientificOutcome:
    outcome: str
    score: int
    rationale: str
    evidence_or_assumption: str


@dataclass
class FollowOnOpportunity:
    opportunity_type: str
    fit: str
    rationale: str
    next_step: str
    time_sensitivity: str = "unknown"


@dataclass
class PastProjectMatch:
    project_name: str
    relevance: str
    reusable_lessons: List[str] = field(default_factory=list)
    confidence: str = "medium"


@dataclass
class ScoreItem:
    name: str
    score: int
    weight: int
    rationale: str


@dataclass
class ReviewFinding:
    severity: str
    finding: str
    recommendation: str


@dataclass
class EOIAssessment:
    scope_rating: str = ""
    scope_summary: str = ""
    design_approach_assessment: str = ""
    technical_components: List[str] = field(default_factory=list)
    technical_feasibility_rating: str = ""
    technical_feasibility_comment: str = ""
    swe_goal_impact_rating: str = ""
    scientific_field_impact_rating: str = ""
    impact_comment: str = ""
    development_readiness: str = ""
    project_types: List[str] = field(default_factory=list)
    engagement_models: List[str] = field(default_factory=list)
    engagement_model_rationale: str = ""
    viss_pairing_recommendation: str = ""
    general_comments: str = ""
    critical_questions: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "EOIAssessment":
        return cls(
            scope_rating=str(payload.get("scope_rating", "")).strip(),
            scope_summary=str(payload.get("scope_summary", "")).strip(),
            design_approach_assessment=str(payload.get("design_approach_assessment", "")).strip(),
            technical_components=_string_list(payload.get("technical_components")),
            technical_feasibility_rating=str(payload.get("technical_feasibility_rating", "")).strip(),
            technical_feasibility_comment=str(payload.get("technical_feasibility_comment", "")).strip(),
            swe_goal_impact_rating=str(payload.get("swe_goal_impact_rating", "")).strip(),
            scientific_field_impact_rating=str(payload.get("scientific_field_impact_rating", "")).strip(),
            impact_comment=str(payload.get("impact_comment", "")).strip(),
            development_readiness=str(payload.get("development_readiness", "")).strip(),
            project_types=_string_list(payload.get("project_types")),
            engagement_models=_string_list(payload.get("engagement_models")),
            engagement_model_rationale=str(payload.get("engagement_model_rationale", "")).strip(),
            viss_pairing_recommendation=str(payload.get("viss_pairing_recommendation", "")).strip(),
            general_comments=str(payload.get("general_comments", "")).strip(),
            critical_questions=_string_list(payload.get("critical_questions")),
        )


@dataclass
class EngagementProfile:
    source_name: str
    title: str = ""
    pi_team: List[Investigator] = field(default_factory=list)
    institutions: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    scientific_domain: str = ""
    scientific_objectives: List[str] = field(default_factory=list)
    software_objectives: List[str] = field(default_factory=list)
    existing_assets: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    data_considerations: List[str] = field(default_factory=list)
    deadlines: List[str] = field(default_factory=list)
    requested_engagement_type: str = ""
    prior_relationships: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)
    capability_matches: List[CapabilityMatch] = field(default_factory=list)
    collaboration_risks: List[CollaborationRisk] = field(default_factory=list)
    scientific_outcomes: List[ScientificOutcome] = field(default_factory=list)
    follow_on_opportunities: List[FollowOnOpportunity] = field(default_factory=list)
    past_project_matches: List[PastProjectMatch] = field(default_factory=list)
    eoi_assessment: Optional[EOIAssessment] = None
    scorecard: List[ScoreItem] = field(default_factory=list)
    recommendation_decision: str = ""
    review_findings: List[ReviewFinding] = field(default_factory=list)

    @classmethod
    def from_agent_payload(cls, payload: Dict[str, Any], source_name: str) -> "EngagementProfile":
        profile = cls(
            source_name=source_name,
            title=str(payload.get("title", "")).strip(),
            pi_team=[
                Investigator.from_dict(item)
                for item in _mapping_list(payload.get("pi_team"))
                if str(item.get("name", "")).strip()
            ],
            institutions=_string_list(payload.get("institutions")),
            locations=_string_list(payload.get("locations")),
            scientific_domain=str(payload.get("scientific_domain", "")).strip(),
            scientific_objectives=_string_list(payload.get("scientific_objectives")),
            software_objectives=_string_list(payload.get("software_objectives")),
            existing_assets=_string_list(payload.get("existing_assets")),
            constraints=_string_list(payload.get("constraints")),
            data_considerations=_string_list(payload.get("data_considerations")),
            deadlines=_string_list(payload.get("deadlines")),
            requested_engagement_type=str(payload.get("requested_engagement_type", "")).strip(),
            prior_relationships=_string_list(payload.get("prior_relationships")),
            open_questions=_string_list(payload.get("open_questions")),
            evidence=[
                EvidenceItem.from_dict(item, source_name)
                for item in _mapping_list(payload.get("evidence"))
                if str(item.get("claim", "")).strip()
            ],
        )

        for investigator in profile.pi_team:
            if investigator.institution and investigator.institution not in profile.institutions:
                profile.institutions.append(investigator.institution)
            if investigator.location and investigator.location not in profile.locations:
                profile.locations.append(investigator.location)

        return profile

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary_markdown(self) -> str:
        lines = [
            f"## Engagement Profile: {self.title or self.source_name}",
            "",
            f"**Recommended decision:** {self.recommendation_decision or 'Pending'}",
            "",
            "### PI Team",
        ]
        if self.pi_team:
            for investigator in self.pi_team:
                details = ", ".join(
                    item
                    for item in [
                        investigator.role,
                        investigator.institution,
                        investigator.location,
                        investigator.time_zone,
                    ]
                    if item
                )
                lines.append(f"- {investigator.name}{f' ({details})' if details else ''}")
        else:
            lines.append("- Not identified")

        sections = [
            ("Scientific Objectives", self.scientific_objectives),
            ("Software Objectives", self.software_objectives),
            ("Existing Assets", self.existing_assets),
            ("Constraints", self.constraints),
            ("Data Considerations", self.data_considerations),
            ("Deadlines", self.deadlines),
            ("Open Questions", self.open_questions),
        ]
        for heading, items in sections:
            lines.extend(["", f"### {heading}"])
            if items:
                lines.extend(f"- {item}" for item in items)
            else:
                lines.append("- Not identified")

        if self.capability_matches:
            lines.extend(["", "### GT VISS / CSSE Capability Fit"])
            for match in self.capability_matches:
                lines.append(f"- **{match.name}** ({match.category}, {match.score}/100): {match.rationale}")

        if self.collaboration_risks:
            lines.extend(["", "### Collaboration Risks"])
            for risk in self.collaboration_risks:
                lines.append(f"- **{risk.severity.upper()} - {risk.name}:** {risk.rationale} Mitigation: {risk.mitigation}")

        if self.scientific_outcomes:
            lines.extend(["", "### Scientific Outcomes"])
            for outcome in self.scientific_outcomes:
                lines.append(f"- **{outcome.outcome}** ({outcome.score}/5): {outcome.rationale}")

        if self.follow_on_opportunities:
            lines.extend(["", "### Follow-On Opportunities"])
            for opportunity in self.follow_on_opportunities:
                lines.append(
                    f"- **{opportunity.opportunity_type}** ({opportunity.fit}): "
                    f"{opportunity.rationale} Next step: {opportunity.next_step}"
                )

        if self.eoi_assessment:
            assessment = self.eoi_assessment
            lines.extend(["", "### VISS Review Rubric Assessment"])
            assessment_items = [
                ("Scope", assessment.scope_rating),
                ("Technical Feasibility", assessment.technical_feasibility_rating),
                ("SWE Goal Impact", assessment.swe_goal_impact_rating),
                ("Scientific Field Impact", assessment.scientific_field_impact_rating),
                ("Development Readiness", assessment.development_readiness),
                ("VISS Pairing Recommendation", assessment.viss_pairing_recommendation),
            ]
            for label, value in assessment_items:
                lines.append(f"- **{label}:** {value or 'Not assessed'}")
            if assessment.scope_summary:
                lines.append(f"- **Scope Summary:** {assessment.scope_summary}")
            if assessment.technical_components:
                lines.append(f"- **Technical Components:** {', '.join(assessment.technical_components)}")
            if assessment.project_types:
                lines.append(f"- **Project Types:** {', '.join(assessment.project_types)}")
            if assessment.engagement_models:
                lines.append(f"- **Potential Engagement Models:** {', '.join(assessment.engagement_models)}")
            if assessment.critical_questions:
                lines.extend(["", "### Rubric Critical Questions"])
                lines.extend(f"- {question}" for question in assessment.critical_questions)

        if self.scorecard:
            lines.extend(["", "### Scorecard"])
            for score in self.scorecard:
                lines.append(f"- **{score.name}** ({score.score}/100, weight {score.weight}%): {score.rationale}")

        if self.review_findings:
            lines.extend(["", "### Agent Review Findings"])
            for finding in self.review_findings:
                lines.append(f"- **{finding.severity.upper()}:** {finding.finding} Recommendation: {finding.recommendation}")

        return "\n".join(lines).strip()

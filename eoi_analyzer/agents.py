import json
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from zoneinfo import ZoneInfo

from .knowledge import past_project_terms, team_context_summary
from .prompting import PromptLibrary
from .profile import (
    CapabilityMatch,
    CollaborationRisk,
    EOIAssessment,
    EngagementProfile,
    EvidenceItem,
    FollowOnOpportunity,
    PastProjectMatch,
    ReviewFinding,
    ScientificOutcome,
    ScoreItem,
)


RunChat = Callable[[List[Dict[str, Any]], float], str]


def extract_json_object(text: str) -> Dict[str, Any]:
    """
    Extract a JSON object from a model response.
    """
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response.")
    return json.loads(candidate[start : end + 1])


def _joined_profile_text(profile: EngagementProfile) -> str:
    values = [
        profile.title,
        profile.scientific_domain,
        profile.requested_engagement_type,
        *profile.scientific_objectives,
        *profile.software_objectives,
        *profile.existing_assets,
        *profile.constraints,
        *profile.data_considerations,
        *profile.deadlines,
        *profile.open_questions,
    ]
    for investigator in profile.pi_team:
        values.extend([investigator.name, investigator.role, investigator.institution, investigator.location])
    return " ".join(value.lower() for value in values if value)


def _keyword_score(text: str, keywords: List[str]) -> int:
    score = 0
    for keyword in keywords:
        if keyword.lower() in text:
            score += 20 if " " in keyword else 10
    return min(100, score)


class DocumentIntakeAgent:
    def __init__(self, run_chat: RunChat, team_context: Dict[str, Any], prompts: PromptLibrary = None):
        self.run_chat = run_chat
        self.team_context = team_context
        self.prompts = prompts or PromptLibrary()

    def run(self, text: str, source_name: str) -> EngagementProfile:
        messages = [
            {
                "role": "system",
                "content": self.prompts.render("document_intake_system.md"),
            },
            {
                "role": "user",
                "content": self.prompts.render(
                    "document_intake_user.md",
                    team_context=team_context_summary(self.team_context),
                    source_name=source_name,
                    document_text=text,
                ),
            },
        ]
        response = self.run_chat(messages, 0.1)
        try:
            payload = extract_json_object(response)
        except Exception:
            profile = EngagementProfile(
                source_name=source_name,
                title=source_name,
                open_questions=[
                    "The intake agent could not return a valid structured profile. Review the source document manually."
                ],
                evidence=[
                    EvidenceItem(
                        claim="Source document was provided for analysis.",
                        source=source_name,
                        quote=text[:500],
                        confidence="low",
                    )
                ],
            )
            return profile
        return EngagementProfile.from_agent_payload(payload, source_name)


class CapabilityMatcherAgent:
    def __init__(self, team_context: Dict[str, Any]):
        self.team_context = team_context

    def run(self, profile: EngagementProfile) -> EngagementProfile:
        text = _joined_profile_text(profile)
        matches: List[CapabilityMatch] = []

        for mode in self.team_context.get("engagement_modes", []):
            score = _keyword_score(text, mode.get("keywords", []))
            if profile.requested_engagement_type and mode["name"].lower() in profile.requested_engagement_type.lower():
                score = min(100, score + 30)
            if score > 0:
                matches.append(
                    CapabilityMatch(
                        name=mode["name"],
                        category="Engagement mode",
                        score=score,
                        rationale=mode.get("description", ""),
                    )
                )

        for skill in self.team_context.get("skill_profiles", []):
            score = _keyword_score(text, skill.get("keywords", []))
            if score > 0:
                matches.append(
                    CapabilityMatch(
                        name=skill["name"],
                        category="Skill profile",
                        score=score,
                        rationale=skill.get("description", ""),
                    )
                )

        if not matches:
            matches.append(
                CapabilityMatch(
                    name="Discovery / Consulting",
                    category="Engagement mode",
                    score=35,
                    rationale="The document does not contain enough software detail to choose a stronger engagement mode.",
                )
            )

        profile.capability_matches = sorted(matches, key=lambda item: item.score, reverse=True)[:6]
        return profile


def infer_time_zone(location: str) -> str:
    lowered = location.lower()
    mappings = [
        ("atlanta", "America/New_York"),
        ("georgia", "America/New_York"),
        ("new york", "America/New_York"),
        ("boston", "America/New_York"),
        ("washington", "America/New_York"),
        ("california", "America/Los_Angeles"),
        ("san francisco", "America/Los_Angeles"),
        ("seattle", "America/Los_Angeles"),
        ("cambridge", "Europe/London"),
        ("london", "Europe/London"),
        ("united kingdom", "Europe/London"),
        ("uk", "Europe/London"),
        ("europe", "Europe/Paris"),
        ("india", "Asia/Kolkata"),
        ("japan", "Asia/Tokyo"),
        ("australia", "Australia/Sydney"),
    ]
    for token, time_zone in mappings:
        if token in lowered:
            return time_zone
    return ""


def business_hour_overlap_hours(time_zone: str, home_time_zone: str) -> Optional[int]:
    if not time_zone:
        return None
    try:
        now = datetime.now(ZoneInfo("UTC"))
        home_offset = now.astimezone(ZoneInfo(home_time_zone)).utcoffset()
        remote_offset = now.astimezone(ZoneInfo(time_zone)).utcoffset()
    except Exception:
        return None
    if home_offset is None or remote_offset is None:
        return None
    delta = int((remote_offset - home_offset).total_seconds() / 3600)
    remote_hours_in_home = {hour - delta for hour in range(9, 17)}
    home_hours = set(range(9, 17))
    return len(home_hours.intersection(remote_hours_in_home))


class CollaborationRiskAgent:
    def __init__(self, team_context: Dict[str, Any]):
        self.team_context = team_context

    def run(self, profile: EngagementProfile) -> EngagementProfile:
        risks: List[CollaborationRisk] = []
        home_time_zone = self.team_context.get("home_time_zone", "America/New_York")

        for investigator in profile.pi_team:
            if not investigator.time_zone and investigator.location:
                investigator.time_zone = infer_time_zone(investigator.location)

        pi_count = len(profile.pi_team)
        if pi_count == 0:
            risks.append(
                CollaborationRisk(
                    name="PI ownership unknown",
                    severity="high",
                    rationale="The document does not identify a clear PI or decision owner.",
                    mitigation="Confirm the accountable PI, technical point of contact, and approval path before committing effort.",
                )
            )
        elif pi_count >= 3:
            risks.append(
                CollaborationRisk(
                    name="Multi-PI coordination",
                    severity="medium",
                    rationale=f"The document names {pi_count} investigators, which can slow requirements and acceptance decisions.",
                    mitigation="Set one accountable PI, one technical delegate, and a decision cadence in the kickoff plan.",
                )
            )

        location_count = len({location for location in profile.locations if location})
        if location_count > 1:
            risks.append(
                CollaborationRisk(
                    name="Distributed stakeholder locations",
                    severity="medium",
                    rationale=f"The profile includes {location_count} distinct locations, raising coordination overhead.",
                    mitigation="Use written decision logs, rotating meeting times if needed, and asynchronous review windows.",
                )
            )

        for investigator in profile.pi_team:
            overlap = business_hour_overlap_hours(investigator.time_zone, home_time_zone)
            if overlap is not None and overlap < 3:
                risks.append(
                    CollaborationRisk(
                        name=f"Limited time-zone overlap with {investigator.name}",
                        severity="medium",
                        rationale=(
                            f"{investigator.location or investigator.time_zone} has roughly {overlap} overlapping "
                            "business hours with Atlanta."
                        ),
                        mitigation="Plan asynchronous reviews and reserve recurring overlap windows for decisions.",
                    )
                )

        if not profile.prior_relationships:
            risks.append(
                CollaborationRisk(
                    name="No prior working relationship identified",
                    severity="medium",
                    rationale="The document does not mention past collaboration with GT CSSE/VISS or the project team.",
                    mitigation="Start with discovery, expectation setting, and a short technical assessment before delivery commitments.",
                )
            )

        if not profile.deadlines:
            risks.append(
                CollaborationRisk(
                    name="Timeline ambiguity",
                    severity="medium",
                    rationale="No clear deadline or external milestone was identified.",
                    mitigation="Define target review, prototype, and handoff dates before writing the final LoI.",
                )
            )

        if profile.data_considerations:
            risks.append(
                CollaborationRisk(
                    name="Data access and governance",
                    severity="medium",
                    rationale="The document mentions data considerations that may affect development, testing, or sharing.",
                    mitigation="Confirm data access, privacy, licensing, compute, and storage constraints during discovery.",
                )
            )

        profile.collaboration_risks = risks
        return profile


class ScientificOutcomeAgent:
    def __init__(self, run_chat: RunChat, team_context: Dict[str, Any], prompts: PromptLibrary = None):
        self.run_chat = run_chat
        self.team_context = team_context
        self.prompts = prompts or PromptLibrary()

    def run(self, profile: EngagementProfile, text: str) -> EngagementProfile:
        messages = [
            {
                "role": "system",
                "content": self.prompts.render("scientific_outcome_system.md"),
            },
            {
                "role": "user",
                "content": self.prompts.render(
                    "scientific_outcome_user.md",
                    team_context=team_context_summary(self.team_context),
                    profile_json=json.dumps(profile.to_dict(), indent=2),
                    document_text=text,
                ),
            },
        ]
        try:
            payload = extract_json_object(self.run_chat(messages, 0.15))
        except Exception:
            profile.scientific_outcomes = [
                ScientificOutcome(
                    outcome="Scientific outcome requires manual review",
                    score=2,
                    rationale="The scientific outcome agent could not return structured output.",
                    evidence_or_assumption="Assumption based on failed structured response.",
                )
            ]
            profile.follow_on_opportunities = [
                FollowOnOpportunity(
                    opportunity_type="Discovery follow-up",
                    fit="medium",
                    rationale="A structured scientific and funding assessment is needed before proposal planning.",
                    next_step="Clarify the expected publication, dataset, platform, or proposal outcome with the PI team.",
                )
            ]
            return profile
        profile.scientific_outcomes = [
            ScientificOutcome(
                outcome=str(item.get("outcome", "")).strip(),
                score=max(1, min(5, int(item.get("score", 1) or 1))),
                rationale=str(item.get("rationale", "")).strip(),
                evidence_or_assumption=str(item.get("evidence_or_assumption", "")).strip(),
            )
            for item in payload.get("scientific_outcomes", [])
            if isinstance(item, dict) and str(item.get("outcome", "")).strip()
        ]
        profile.follow_on_opportunities = [
            FollowOnOpportunity(
                opportunity_type=str(item.get("opportunity_type", "")).strip(),
                fit=str(item.get("fit", "medium")).strip() or "medium",
                rationale=str(item.get("rationale", "")).strip(),
                next_step=str(item.get("next_step", "")).strip(),
                time_sensitivity=str(item.get("time_sensitivity", "unknown")).strip() or "unknown",
            )
            for item in payload.get("follow_on_opportunities", [])
            if isinstance(item, dict) and str(item.get("opportunity_type", "")).strip()
        ]
        return profile


class EOIAssessmentAgent:
    def __init__(self, run_chat: RunChat, team_context: Dict[str, Any], prompts: PromptLibrary = None):
        self.run_chat = run_chat
        self.team_context = team_context
        self.prompts = prompts or PromptLibrary()

    def run(self, profile: EngagementProfile, text: str) -> EngagementProfile:
        messages = [
            {
                "role": "system",
                "content": self.prompts.render("eoi_assessment_system.md"),
            },
            {
                "role": "user",
                "content": self.prompts.render(
                    "eoi_assessment_user.md",
                    team_context=team_context_summary(self.team_context),
                    profile_json=json.dumps(profile.to_dict(), indent=2),
                    document_text=text,
                ),
            },
        ]
        try:
            payload = extract_json_object(self.run_chat(messages, 0.1))
            profile.eoi_assessment = EOIAssessment.from_dict(payload)
        except Exception:
            profile.eoi_assessment = self._fallback_assessment(profile)
        return profile

    def _fallback_assessment(self, profile: EngagementProfile) -> EOIAssessment:
        scope_rating = (
            "The scope is clear and well-defined"
            if profile.scientific_objectives and profile.software_objectives and profile.deadlines
            else "The scope is somewhat defined, but requires further clarification"
        )
        feasibility_rating = (
            "Technically feasible with the required expertise and can be completed within the 3-9 month timeline."
            if profile.software_objectives and profile.deadlines
            else "Somewhat technically feasible but requires additional expertise or significant effort to meet the 3-9 month timeline."
        )
        swe_impact = (
            "Proposed SWE work may significantly address project's goals"
            if profile.software_objectives and profile.scientific_objectives
            else "Proposed SWE work may minimally address the project's goals"
        )
        scientific_impact = (
            "Proposed work may result in significant impacts on their scientific research field"
            if profile.scientific_outcomes
            else "Impact of the proposed work is absent, unclear, or insignificant"
        )
        readiness = (
            "Requires Further Discussion"
            if profile.open_questions or profile.collaboration_risks
            else "Yes"
        )
        recommendation = (
            "Yes, pending on responses to follow-up questions"
            if readiness == "Requires Further Discussion"
            else "Yes"
        )
        return EOIAssessment(
            scope_rating=scope_rating,
            scope_summary=profile.title or "The project requires manual scope review.",
            design_approach_assessment="Fallback assessment generated from the structured engagement profile.",
            technical_components=self._infer_technical_components(profile),
            technical_feasibility_rating=feasibility_rating,
            technical_feasibility_comment="Review manually because the rubric assessment agent did not return structured output.",
            swe_goal_impact_rating=swe_impact,
            scientific_field_impact_rating=scientific_impact,
            impact_comment="Derived from extracted objectives and scientific outcome profile.",
            development_readiness=readiness,
            project_types=self._infer_project_types(profile),
            engagement_models=["Spec-driven development"] if profile.open_questions else ["Maintenance and handover"],
            engagement_model_rationale="Selected conservatively from profile clarity and open questions.",
            viss_pairing_recommendation=recommendation,
            general_comments="Fallback rubric assessment; confirm during EOI review.",
            critical_questions=profile.open_questions,
        )

    def _infer_technical_components(self, profile: EngagementProfile) -> List[str]:
        text = _joined_profile_text(profile)
        component_keywords = {
            "Cloud": ["cloud", "aws", "azure", "gcp"],
            "Data management and storage": ["data", "storage", "database", "repository"],
            "AI/ML": ["ai", "ml", "machine learning", "model", "genai", "llm"],
            "Software architecture and refactoring": ["architecture", "refactor", "rewrite"],
            "Scientific computing and performance/HPC": ["hpc", "performance", "gpu", "simulation"],
            "Packaging and distribution": ["package", "distribution", "release"],
            "Visualization and user interfaces": ["visualization", "ui", "ux", "dashboard"],
            "Workflow and pipeline automation": ["workflow", "pipeline", "automation"],
            "Documentation and open source release": ["documentation", "open source", "readme"],
        }
        components = [
            component
            for component, keywords in component_keywords.items()
            if any(keyword in text for keyword in keywords)
        ]
        return components or ["Other"]

    def _infer_project_types(self, profile: EngagementProfile) -> List[str]:
        text = _joined_profile_text(profile)
        project_types = []
        if any(token in text for token in ["new", "prototype", "mvp", "feature"]):
            project_types.append("New functionality")
        if any(token in text for token in ["production", "harden", "deploy", "release"]):
            project_types.append("Productionalize")
        if any(token in text for token in ["profile", "performance", "optimize"]):
            project_types.append("Profile")
        if any(token in text for token in ["ui", "ux", "dashboard", "visualization"]):
            project_types.append("UI/UX")
        if any(token in text for token in ["scale", "scaling", "hpc", "gpu"]):
            project_types.append("Scale")
        return project_types or ["New functionality"]


class PastProjectMatcherAgent:
    def __init__(self, team_context: Dict[str, Any]):
        self.team_context = team_context

    def run(self, profile: EngagementProfile) -> EngagementProfile:
        projects = self.team_context.get("past_projects", [])
        if not isinstance(projects, list) or not projects:
            return profile

        profile_terms = set(_joined_profile_text(profile).split())
        matches: List[PastProjectMatch] = []
        for project in projects:
            if not isinstance(project, dict):
                continue
            project_terms = set(past_project_terms(project))
            overlap = sorted(profile_terms.intersection(project_terms))
            if len(overlap) < 2:
                continue
            matches.append(
                PastProjectMatch(
                    project_name=str(project.get("name", "Unnamed project")),
                    relevance=f"Shared terms: {', '.join(overlap[:8])}",
                    reusable_lessons=[
                        str(lesson)
                        for lesson in project.get("lessons", [])
                        if str(lesson).strip()
                    ][:5],
                    confidence="high" if len(overlap) >= 5 else "medium",
                )
            )
        profile.past_project_matches = matches[:5]
        return profile


class ScorecardAgent:
    WEIGHTS = {
        "Scientific impact": 25,
        "Engineering leverage": 20,
        "Fit to GT VISS / CSSE capabilities": 20,
        "Execution feasibility": 15,
        "Collaboration readiness": 10,
        "Follow-on proposal potential": 10,
    }

    def run(self, profile: EngagementProfile) -> EngagementProfile:
        scientific_score = 50
        if profile.scientific_outcomes:
            scientific_score = int(sum(item.score for item in profile.scientific_outcomes) / len(profile.scientific_outcomes) * 20)
        if profile.eoi_assessment:
            scientific_score = max(
                scientific_score,
                self._scientific_field_impact_score(profile.eoi_assessment.scientific_field_impact_rating),
            )

        engineering_score = 40
        if profile.software_objectives:
            engineering_score += 25
        if profile.existing_assets:
            engineering_score += 15
        if profile.data_considerations:
            engineering_score += 5
        if profile.eoi_assessment:
            engineering_score = max(
                engineering_score,
                self._swe_goal_impact_score(profile.eoi_assessment.swe_goal_impact_rating),
            )
        engineering_score = min(100, engineering_score)

        fit_score = max([match.score for match in profile.capability_matches], default=35)

        high_risks = sum(1 for risk in profile.collaboration_risks if risk.severity == "high")
        medium_risks = sum(1 for risk in profile.collaboration_risks if risk.severity == "medium")
        feasibility_score = max(10, 90 - high_risks * 30 - medium_risks * 10)
        if profile.eoi_assessment:
            feasibility_score = min(
                feasibility_score,
                self._technical_feasibility_score(profile.eoi_assessment.technical_feasibility_rating),
            )

        readiness_score = max(10, 100 - high_risks * 35 - medium_risks * 15)
        if profile.prior_relationships:
            readiness_score = min(100, readiness_score + 10)
        if profile.eoi_assessment:
            readiness_score = min(
                readiness_score,
                self._readiness_score(profile.eoi_assessment.development_readiness),
            )

        follow_on_score = 35
        if profile.follow_on_opportunities:
            fit_values = {"high": 30, "medium": 20, "low": 10}
            follow_on_score = min(
                100,
                40 + sum(fit_values.get(item.fit.lower(), 20) for item in profile.follow_on_opportunities[:3]),
            )

        scores = [
            ScoreItem("Scientific impact", scientific_score, self.WEIGHTS["Scientific impact"], "Based on stated or inferred scientific outcomes."),
            ScoreItem("Engineering leverage", engineering_score, self.WEIGHTS["Engineering leverage"], "Based on software objectives, assets, and engineering surface area."),
            ScoreItem("Fit to GT VISS / CSSE capabilities", fit_score, self.WEIGHTS["Fit to GT VISS / CSSE capabilities"], "Based on matched engagement modes and skill profiles."),
            ScoreItem("Execution feasibility", feasibility_score, self.WEIGHTS["Execution feasibility"], "Reduced by unresolved delivery risks."),
            ScoreItem("Collaboration readiness", readiness_score, self.WEIGHTS["Collaboration readiness"], "Reduced by PI, timezone, decision, and relationship ambiguity."),
            ScoreItem("Follow-on proposal potential", follow_on_score, self.WEIGHTS["Follow-on proposal potential"], "Based on proposal, platform, fellowship, or sustainability pathways."),
        ]
        profile.scorecard = scores

        weighted_total = sum(score.score * score.weight for score in scores) / 100
        if weighted_total >= 75 and high_risks == 0:
            profile.recommendation_decision = "Proceed"
        elif weighted_total >= 60:
            profile.recommendation_decision = "Proceed with conditions"
        elif weighted_total >= 45:
            profile.recommendation_decision = "Discovery first"
        else:
            profile.recommendation_decision = "Defer until clarified"
        if profile.eoi_assessment:
            profile.recommendation_decision = self._apply_pairing_recommendation(
                profile.recommendation_decision,
                profile.eoi_assessment.viss_pairing_recommendation,
            )
        return profile

    @staticmethod
    def _technical_feasibility_score(value: str) -> int:
        if value.startswith("Technically feasible"):
            return 85
        if value.startswith("Somewhat technically feasible"):
            return 60
        if value.startswith("Not technically feasible"):
            return 20
        return 60

    @staticmethod
    def _swe_goal_impact_score(value: str) -> int:
        if value.startswith("Proposed SWE work may significantly"):
            return 85
        if value.startswith("Proposed SWE work may minimally"):
            return 50
        if value.startswith("The potential impact"):
            return 20
        return 50

    @staticmethod
    def _scientific_field_impact_score(value: str) -> int:
        if value.startswith("Proposed work has the potential to substantially"):
            return 95
        if value.startswith("Proposed work may result in significant"):
            return 80
        if value.startswith("Proposed work may result in minor"):
            return 50
        if value.startswith("Impact of the proposed work"):
            return 20
        return 50

    @staticmethod
    def _readiness_score(value: str) -> int:
        if value == "Yes":
            return 90
        if value == "Requires Further Discussion":
            return 55
        if value == "No":
            return 20
        return 55

    @staticmethod
    def _apply_pairing_recommendation(current: str, pairing_recommendation: str) -> str:
        if pairing_recommendation == "Yes":
            return current
        if pairing_recommendation == "Yes, pending on responses to follow-up questions":
            return "Proceed with conditions" if current == "Proceed" else current
        if pairing_recommendation == "No":
            return "Defer until clarified"
        return current


class ProfileReviewAgent:
    def __init__(self, team_context: Dict[str, Any]):
        self.team_context = team_context

    def run(self, profile: EngagementProfile) -> EngagementProfile:
        findings: List[ReviewFinding] = []

        if not profile.pi_team:
            findings.append(
                ReviewFinding("high", "No PI team was extracted.", "Ask for PI name, role, institution, and decision authority.")
            )
        if not profile.locations:
            findings.append(
                ReviewFinding("medium", "PI or collaborator locations are missing.", "Confirm locations and time zones before finalizing collaboration cadence.")
            )
        if not profile.software_objectives:
            findings.append(
                ReviewFinding("high", "Software objectives are unclear.", "Run discovery before committing to a project plan or LoI scope.")
            )
        if not profile.scientific_objectives:
            findings.append(
                ReviewFinding("high", "Scientific objectives are unclear.", "Clarify the scientific outcome the software work should enable.")
            )
        if not profile.deadlines:
            findings.append(
                ReviewFinding("medium", "No deadlines or external proposal milestones were found.", "Confirm target dates for kickoff, prototype review, and proposal follow-up.")
            )
        if not profile.past_project_matches:
            findings.append(
                ReviewFinding(
                    "low",
                    "No local past-project matches were available.",
                    "Provide a team context JSON file with prior projects to improve matching and reuse recommendations.",
                )
            )
        if len(profile.evidence) < 3:
            findings.append(
                ReviewFinding(
                    "medium",
                    "The evidence set is thin.",
                    "Treat factual claims cautiously and ask for the original EoI details during intake review.",
                )
            )

        profile.review_findings = findings
        return profile

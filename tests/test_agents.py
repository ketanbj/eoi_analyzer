import json

from eoi_analyzer.agents import (
    CapabilityMatcherAgent,
    CollaborationRiskAgent,
    DocumentIntakeAgent,
    EOIAssessmentAgent,
    ScorecardAgent,
    extract_json_object,
)
from eoi_analyzer.knowledge import load_team_context
from eoi_analyzer.profile import EngagementProfile, Investigator, ScientificOutcome


def test_extract_json_object_handles_fenced_nested_json():
    payload = extract_json_object(
        """```json
        {"items": [{"name": "alpha", "values": [1, 2, 3]}]}
        ```"""
    )

    assert payload == {"items": [{"name": "alpha", "values": [1, 2, 3]}]}


def test_document_intake_agent_builds_profile_from_json_response():
    def run_chat(messages, temperature):
        return json.dumps(
            {
                "title": "Microscopy workflow",
                "pi_team": [
                    {
                        "name": "Dr. Ada Chen",
                        "role": "PI",
                        "institution": "Georgia Tech",
                        "location": "Atlanta, GA",
                        "time_zone": "",
                        "evidence": "Dr. Ada Chen at Georgia Tech",
                    }
                ],
                "institutions": [],
                "locations": [],
                "scientific_domain": "bioimaging",
                "scientific_objectives": ["Improve reproducibility"],
                "software_objectives": ["Build an MVP workflow"],
                "existing_assets": ["Python notebooks"],
                "constraints": ["Three-month prototype review"],
                "data_considerations": ["Controlled-access images"],
                "deadlines": ["Three-month prototype review"],
                "requested_engagement_type": "MVP prototyping",
                "prior_relationships": [],
                "open_questions": ["Who maintains the workflow?"],
                "evidence": [
                    {
                        "claim": "The team needs an MVP",
                        "source": "eoi.txt",
                        "quote": "Build an MVP workflow",
                        "confidence": "high",
                    }
                ],
            }
        )

    profile = DocumentIntakeAgent(run_chat, load_team_context()).run("text", "eoi.txt")

    assert profile.title == "Microscopy workflow"
    assert profile.pi_team[0].name == "Dr. Ada Chen"
    assert profile.institutions == ["Georgia Tech"]
    assert profile.locations == ["Atlanta, GA"]
    assert profile.software_objectives == ["Build an MVP workflow"]


def test_document_intake_agent_falls_back_on_invalid_json():
    def run_chat(messages, temperature):
        return "not json"

    profile = DocumentIntakeAgent(run_chat, load_team_context()).run("source text", "broken.txt")

    assert profile.title == "broken.txt"
    assert profile.open_questions
    assert profile.evidence[0].confidence == "low"


def test_capability_matcher_matches_gt_capabilities():
    profile = EngagementProfile(
        source_name="eoi.txt",
        requested_engagement_type="MVP prototyping",
        software_objectives=[
            "Build a prototype Python workflow with tests, documentation, and deployment"
        ],
    )

    CapabilityMatcherAgent(load_team_context()).run(profile)

    names = {match.name for match in profile.capability_matches}
    assert "Prototyping" in names
    assert any(match.category == "Skill profile" for match in profile.capability_matches)


def test_collaboration_risk_agent_flags_multi_pi_and_distributed_locations():
    profile = EngagementProfile(
        source_name="eoi.txt",
        pi_team=[
            Investigator("Dr. A", location="Atlanta, GA"),
            Investigator("Dr. B", location="Cambridge, UK"),
            Investigator("Dr. C", location="India"),
        ],
        locations=["Atlanta, GA", "Cambridge, UK", "India"],
        data_considerations=["Controlled data"],
    )

    CollaborationRiskAgent(load_team_context()).run(profile)

    risk_names = {risk.name for risk in profile.collaboration_risks}
    assert "Multi-PI coordination" in risk_names
    assert "Distributed stakeholder locations" in risk_names
    assert "Data access and governance" in risk_names


def test_scorecard_sets_decision_from_profile_signals():
    profile = EngagementProfile(
        source_name="eoi.txt",
        software_objectives=["Build a tested workflow"],
        existing_assets=["Prototype notebooks"],
        prior_relationships=["Worked with GT CSSE previously"],
        scientific_outcomes=[
            ScientificOutcome(
                outcome="Reproducible analysis",
                score=4,
                rationale="Strong scientific benefit",
                evidence_or_assumption="stated",
            )
        ],
    )
    CapabilityMatcherAgent(load_team_context()).run(profile)

    ScorecardAgent().run(profile)

    assert profile.scorecard
    assert profile.recommendation_decision in {"Proceed", "Proceed with conditions"}


def test_eoi_assessment_agent_builds_rubric_assessment():
    def run_chat(messages, temperature):
        return json.dumps(
            {
                "scope_rating": "The scope is clear and well-defined",
                "scope_summary": "Build a workflow automation MVP.",
                "design_approach_assessment": "The approach is sensible.",
                "technical_components": ["Workflow and pipeline automation", "Documentation and open source release"],
                "technical_feasibility_rating": "Technically feasible with the required expertise and can be completed within the 3-9 month timeline.",
                "technical_feasibility_comment": "MVP appears bounded.",
                "swe_goal_impact_rating": "Proposed SWE work may significantly address project's goals",
                "scientific_field_impact_rating": "Proposed work may result in significant impacts on their scientific research field",
                "impact_comment": "Could improve reproducibility.",
                "development_readiness": "Yes",
                "project_types": ["New functionality"],
                "engagement_models": ["Spec-driven development"],
                "engagement_model_rationale": "Requirements should be clarified before implementation.",
                "viss_pairing_recommendation": "Yes",
                "general_comments": "Strong fit.",
                "critical_questions": ["Who owns maintenance?"],
            }
        )

    profile = EngagementProfile(
        source_name="eoi.txt",
        scientific_objectives=["Improve reproducibility"],
        software_objectives=["Build a workflow automation MVP"],
    )

    EOIAssessmentAgent(run_chat, load_team_context()).run(profile, "document")

    assert profile.eoi_assessment.scope_rating == "The scope is clear and well-defined"
    assert "Workflow and pipeline automation" in profile.eoi_assessment.technical_components
    assert profile.eoi_assessment.viss_pairing_recommendation == "Yes"


def test_eoi_assessment_agent_fallback_is_conservative_on_bad_json():
    def run_chat(messages, temperature):
        return "not json"

    profile = EngagementProfile(
        source_name="eoi.txt",
        title="Example EOI",
        open_questions=["What data can be shared?"],
    )

    EOIAssessmentAgent(run_chat, load_team_context()).run(profile, "document")

    assert profile.eoi_assessment.scope_rating == "The scope is somewhat defined, but requires further clarification"
    assert profile.eoi_assessment.development_readiness == "Requires Further Discussion"
    assert profile.eoi_assessment.critical_questions == ["What data can be shared?"]

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_TEAM_CONTEXT: Dict[str, Any] = {
    "name": "Georgia Tech CSSE / VISS",
    "home_time_zone": "America/New_York",
    "mission": (
        "Support better quality, more sustainable scientific software; accelerate scientific "
        "discovery; support long-term platforms and systems; and encourage best practices in open science."
    ),
    "sources": [
        {
            "name": "GT CSSE Center Capabilities",
            "url": "https://ssecenter.cc.gatech.edu/center-capabilities/",
        },
        {
            "name": "GT CSSE About",
            "url": "https://ssecenter.cc.gatech.edu/",
        },
        {
            "name": "Schmidt Sciences VISS",
            "url": "https://www.schmidtsciences.org/viss/",
        },
    ],
    "engagement_modes": [
        {
            "name": "Prototyping",
            "impact_rank": 1,
            "description": "Create MVPs or enhanced software that demonstrate system capabilities.",
            "keywords": ["prototype", "mvp", "proof of concept", "pilot", "demo", "enhance", "new capability"],
        },
        {
            "name": "Partnering",
            "impact_rank": 2,
            "description": "Work side-by-side for a scoped period to define goals and deliver software artifacts.",
            "keywords": ["build", "implement", "deliver", "collaborate", "roadmap", "engineering team", "production"],
        },
        {
            "name": "Guiding",
            "impact_rank": 3,
            "description": "Meet periodically to identify bottlenecks, suggest improvements, and keep work moving.",
            "keywords": ["advise", "guide", "review progress", "bottleneck", "technical direction", "weekly"],
        },
        {
            "name": "Mentoring",
            "impact_rank": 4,
            "description": "Help project team members grow through recurring technical mentorship.",
            "keywords": ["mentor", "student", "postdoc", "training", "upskill", "onboarding"],
        },
        {
            "name": "Consulting",
            "impact_rank": 5,
            "description": "One-time or short advisory engagement around architecture, UX, code, or project risk.",
            "keywords": ["consult", "architecture review", "code review", "ux review", "risk review", "one-off"],
        },
        {
            "name": "Profiling",
            "impact_rank": 6,
            "description": "Identify and propose resolutions to performance bottlenecks.",
            "keywords": ["profile", "performance", "optimize", "bottleneck", "scaling", "hpc", "simulation"],
        },
        {
            "name": "Curriculum Development and Training",
            "impact_rank": 7,
            "description": "Develop and present reusable training for industry and academia.",
            "keywords": ["workshop", "curriculum", "training", "ci/cd", "code review", "testing", "open source"],
        },
    ],
    "skill_profiles": [
        {
            "name": "Software Engineer",
            "description": "Write code and apply best-of-industry practices to solve problems and automate work.",
            "keywords": ["software", "code", "pipeline", "automation", "package", "api", "testing", "ci/cd"],
        },
        {
            "name": "Software Architect",
            "description": "Design software, infrastructure, and technology stacks.",
            "keywords": ["architecture", "infrastructure", "cloud", "hpc", "database", "deployment", "platform"],
        },
        {
            "name": "Product Management",
            "description": "Apply lean software principles to validate hypotheses and introduce MVPs.",
            "keywords": ["mvp", "users", "requirements", "roadmap", "stakeholders", "validation", "adoption"],
        },
        {
            "name": "Program Management",
            "description": "Introduce practices that detect delivery issues before they derail progress.",
            "keywords": ["milestones", "timeline", "governance", "coordination", "dependencies", "multi-team"],
        },
        {
            "name": "UI/UX",
            "description": "Create efficient, engaging, easy-to-use interfaces and workflows.",
            "keywords": ["ui", "ux", "dashboard", "visualization", "interface", "portal", "workflow"],
        },
        {
            "name": "Technical Writer",
            "description": "Communicate complicated software ideas and product details to broad audiences.",
            "keywords": ["documentation", "tutorial", "user guide", "training material", "onboarding", "readme"],
        },
    ],
    "broader_skill_areas": [
        "research software engineering",
        "software architecture",
        "data engineering",
        "AI/ML engineering",
        "MLOps",
        "HPC and performance engineering",
        "cloud and infrastructure engineering",
        "security and privacy review",
        "UI/UX and visualization",
        "testing and quality assurance",
        "technical writing and documentation",
        "open-source governance",
        "community management",
        "training and curriculum development",
        "product management",
        "program management",
        "proposal development",
        "domain-science liaison",
    ],
    "skill_acquisition_channels": [
        "GT CSSE/VISS staff",
        "PI-team domain expertise",
        "students, trainees, or fellows",
        "internal Georgia Tech partners",
        "external scientific collaborators",
        "reusable assets from past projects",
        "open-source community packages or maintainers",
        "vendor or cloud-provider support",
        "targeted workshops or mentoring",
        "future proposal-funded hires or contracts",
    ],
    "funding_opportunity_categories": [
        {
            "name": "Follow-on research proposal",
            "description": "Use prototype or discovery outputs as preliminary work for a larger grant.",
        },
        {
            "name": "Open-source sustainability proposal",
            "description": "Position reusable scientific software as a community or infrastructure asset.",
        },
        {
            "name": "Platform or center-scale opportunity",
            "description": "Elevate multi-lab software infrastructure into a longer-term platform effort.",
        },
        {
            "name": "Student fellowship or trainee project",
            "description": "Convert a prototype into a mentored student or fellow project when appropriate.",
        },
        {
            "name": "Industry or foundation partnership",
            "description": "Pursue external partners when the software enables broader applied impact.",
        },
    ],
    "past_projects": [],
}


def _merge_context(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_context(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_team_context(context_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load default GT CSSE/VISS context, optionally merged with a local JSON file.
    """
    path = context_path or os.getenv("EOI_ANALYZER_TEAM_CONTEXT")
    if not path:
        return deepcopy(DEFAULT_TEAM_CONTEXT)

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Team context file must contain a JSON object.")
    return _merge_context(DEFAULT_TEAM_CONTEXT, payload)


def team_context_summary(context: Dict[str, Any]) -> str:
    modes = ", ".join(mode["name"] for mode in context.get("engagement_modes", []))
    skills = ", ".join(skill["name"] for skill in context.get("skill_profiles", []))
    broader_skills = ", ".join(context.get("broader_skill_areas", []))
    acquisition_channels = ", ".join(context.get("skill_acquisition_channels", []))
    return (
        f"Team: {context.get('name', 'Unknown')}\n"
        f"Mission: {context.get('mission', '')}\n"
        f"Engagement modes: {modes}\n"
        f"Skill profiles: {skills}\n"
        f"Broader skill areas to consider: {broader_skills}\n"
        f"Skill acquisition channels: {acquisition_channels}"
    )


def past_project_terms(project: Dict[str, Any]) -> List[str]:
    terms: List[str] = []
    for key in ["name", "domain", "summary"]:
        value = project.get(key)
        if value:
            terms.extend(str(value).lower().split())
    for key in ["technologies", "outcomes", "lessons"]:
        values = project.get(key, [])
        if isinstance(values, list):
            for value in values:
                terms.extend(str(value).lower().split())
    return terms

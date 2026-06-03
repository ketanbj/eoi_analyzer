import io
import json
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from typing import List, Dict, Any

from .agents import (
    CapabilityMatcherAgent,
    CollaborationRiskAgent,
    DocumentIntakeAgent,
    EOIAssessmentAgent,
    PastProjectMatcherAgent,
    ProfileReviewAgent,
    ScientificOutcomeAgent,
    ScorecardAgent,
)
from .config import OPENAI_MODEL, LITELLM_PROXY_URL
from .knowledge import load_team_context, team_context_summary
from .profile import EngagementProfile
from .prompting import PromptLibrary
from .results import BatchAnalysis, DocumentAnalysis, DocumentFailure
from .utils import extract_text_from_document, iter_document_paths


class EOIAnalyzer:
    """
    Build software-engineering recommendations, project plans, and Letters of Intent
    from Expressions of Interest or related planning documents.
    """

    def __init__(self, openai_api_key, team_context_path=None, prompt_dir=None):
        self.api_key = openai_api_key
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required to run the analyzer.")
        self.base_url = LITELLM_PROXY_URL.rstrip("/")
        self.team_context = load_team_context(team_context_path)
        self.prompts = PromptLibrary(prompt_dir)

    def _run_chat(self, messages: List[Dict[str, Any]], temperature: float = 0.4) -> str:
        """
        Shared helper that calls the configured LiteLLM proxy for chat completions.
        """
        from litellm import completion

        response = completion(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            api_key=self.api_key,
            base_url=self.base_url,
        )
        return response["choices"][0]["message"]["content"].strip()

    def build_engagement_profile(self, text: str, source_name: str) -> EngagementProfile:
        """
        Run the bounded agent pipeline that turns raw document text into a reviewed profile.
        """
        profile = DocumentIntakeAgent(self._run_chat, self.team_context, self.prompts).run(text, source_name)
        profile = CapabilityMatcherAgent(self.team_context).run(profile)
        profile = CollaborationRiskAgent(self.team_context).run(profile)
        profile = ScientificOutcomeAgent(self._run_chat, self.team_context, self.prompts).run(profile, text)
        profile = EOIAssessmentAgent(self._run_chat, self.team_context, self.prompts).run(profile, text)
        profile = PastProjectMatcherAgent(self.team_context).run(profile)
        profile = ScorecardAgent().run(profile)
        profile = ProfileReviewAgent(self.team_context).run(profile)
        return profile

    def generate_engagement_snapshot(self, profile):
        """
        Produce a concise snapshot from an enriched engagement profile.
        """
        if isinstance(profile, EngagementProfile):
            return profile.summary_markdown()

        text = profile
        messages = [
            {
                "role": "system",
                "content": self.prompts.render("engagement_snapshot_system.md"),
            },
            {
                "role": "user",
                "content": self.prompts.render(
                    "engagement_snapshot_user.md",
                    document_text=text,
                ),
            },
        ]
        return self._run_chat(messages, temperature=0.3)

    def generate_recommendation(self, text, profile):
        """
        Recommend how the software engineering team should engage with the project.
        """
        profile_json = json.dumps(profile.to_dict(), indent=2) if isinstance(profile, EngagementProfile) else str(profile)
        messages = [
            {
                "role": "system",
                "content": self.prompts.render("recommendation_system.md"),
            },
            {
                "role": "user",
                "content": self.prompts.render(
                    "recommendation_user.md",
                    team_context=team_context_summary(self.team_context),
                    profile_json=profile_json,
                    document_text=text,
                ),
            },
        ]
        return self._run_chat(messages, temperature=0.25)

    def generate_project_plan(self, text, profile, recommendation):
        """
        Generate a practical project plan for the recommended software engineering engagement.
        """
        profile_json = json.dumps(profile.to_dict(), indent=2) if isinstance(profile, EngagementProfile) else str(profile)
        messages = [
            {
                "role": "system",
                "content": self.prompts.render("project_plan_system.md"),
            },
            {
                "role": "user",
                "content": self.prompts.render(
                    "project_plan_user.md",
                    team_context=team_context_summary(self.team_context),
                    profile_json=profile_json,
                    recommendation=recommendation,
                    document_text=text,
                ),
            },
        ]
        return self._run_chat(messages, temperature=0.25)

    def generate_letter_of_intent(self, text, profile, recommendation=None, project_plan=None):
        """
        Convert the EoI into a Letter of Intent for a 3-6 month software engineering engagement.
        """
        today = date.today().strftime("%B %d, %Y")
        profile_json = json.dumps(profile.to_dict(), indent=2) if isinstance(profile, EngagementProfile) else str(profile)
        messages = [
            {
                "role": "system",
                "content": self.prompts.render("letter_of_intent_system.md"),
            },
            {
                "role": "user",
                "content": self.prompts.render(
                    "letter_of_intent_user.md",
                    today=today,
                    team_context=team_context_summary(self.team_context),
                    profile_json=profile_json,
                    recommendation=recommendation or "",
                    project_plan=project_plan or "",
                    document_text=text,
                ),
            },
        ]
        return self._run_chat(messages, temperature=0.25)

    def analyze_document(self, document_path, include_letter: bool = False):
        """
        Extract text from one document and generate recommendation and project-plan outputs.
        """
        path = Path(document_path)
        log_stream = io.StringIO()
        with redirect_stdout(log_stream):
            print(f"Extracting text from {path.name}...")
            text = extract_text_from_document(path)

            print("Building agentic engagement profile...")
            profile = self.build_engagement_profile(text, path.name)

            print("Rendering engagement snapshot...")
            snapshot = self.generate_engagement_snapshot(profile)

            print("Generating recommendation...")
            recommendation = self.generate_recommendation(text, profile)

            print("Generating project plan...")
            project_plan = self.generate_project_plan(text, profile, recommendation)

            letter = None
            if include_letter:
                print("Drafting Letter of Intent...")
                letter = self.generate_letter_of_intent(text, profile, recommendation, project_plan)

        return DocumentAnalysis(
            source_path=str(path),
            source_name=path.name,
            text_char_count=len(text),
            engagement_snapshot=snapshot,
            recommendation=recommendation,
            project_plan=project_plan,
            letter_of_intent=letter,
            engagement_profile=profile.to_dict(),
            agent_review=profile.summary_markdown(),
            log=log_stream.getvalue(),
        )

    def analyze_pdf(self, pdf_path):
        """
        Backwards-compatible PDF workflow that includes the Letter of Intent draft.
        """
        return self.analyze_document(pdf_path, include_letter=True)

    def analyze_folder(self, folder_path, recursive: bool = True, include_letter: bool = False, extensions=None):
        """
        Analyze every supported document in a folder.
        """
        batch = BatchAnalysis()

        for document_path in iter_document_paths(folder_path, recursive=recursive, extensions=extensions):
            try:
                batch.analyses.append(
                    self.analyze_document(document_path, include_letter=include_letter)
                )
            except Exception as exc:
                batch.failures.append(
                    DocumentFailure(
                        source_path=str(document_path),
                        source_name=document_path.name,
                        error=str(exc),
                    )
                )

        return batch

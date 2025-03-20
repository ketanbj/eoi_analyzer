import io
from contextlib import redirect_stdout
from openai import OpenAI
from .utils import extract_text_from_pdf
from .config import OPENAI_MODEL

class EOIAnalyzer:
    def __init__(self, openai_api_key):
        """
        Initialize the EOI Analyzer with an OpenAI API key.
        """
        self.api_key = openai_api_key
        self.client = OpenAI(api_key=self.api_key)

    def analyze_text_with_openai(self, text, prompt):
        """
        Query OpenAI's model with the provided prompt and text.
        """
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert software engineering product manager."},
                {"role": "user", "content": f"{prompt}\n\n{text}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    def extract_software_goals(self, text):
        prompt = (
            "Analyze the provided document and identify key software engineering goals. "
            "These should include the specific types of software support requested, expected outcomes, "
            "and the scope of software development required. Provide a structured list of goals."
        )
        return self.analyze_text_with_openai(text, prompt)

    def generate_product_management_plan(self, text):
        prompt = (
            "Based on the provided document, create a detailed product management plan outlining the software engineering "
            "tasks required. Include phases, timelines, key deliverables, and potential technical challenges."
        )
        return self.analyze_text_with_openai(text, prompt)

    def generate_potential_risks(self, text):
        prompt = (
            "Based on the provided document, identify potential risks and challenges that could impact the software engineering project. "
            "Include technical, operational, and timeline-related risks."
        )
        return self.analyze_text_with_openai(text, prompt)

    def generate_clarifying_questions(self, text):
        prompt = (
            "After analyzing the document, identify any missing or unclear details that are needed "
            "to create a better software engineering plan. Provide a list of clarifying questions."
        )
        return self.analyze_text_with_openai(text, prompt)

    def analyze_pdf(self, pdf_path):
        """
        Run the full analysis workflow on a given PDF document and capture log output.
        """
        log = io.StringIO()
        with redirect_stdout(log):
            print("Extracting text from PDF...")
            text = extract_text_from_pdf(pdf_path)

            print("Extracting software engineering goals...")
            goals = self.extract_software_goals(text)

            print("Generating product management plan...")
            plan = self.generate_product_management_plan(text)

            print("Identifying potential risks...")
            risks = self.generate_potential_risks(text)

            print("Generating clarifying questions...")
            questions = self.generate_clarifying_questions(text)

        return {
            "software_goals": goals,
            "product_management_plan": plan,
            "potential_risks": risks,
            "clarifying_questions": questions,
            "log": log.getvalue()
        }
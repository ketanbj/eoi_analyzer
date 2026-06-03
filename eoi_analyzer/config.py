import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "https://litellm-dev.pace.gatech.edu:4000/")

SUPPORTED_DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown", ".docx"}
DEFAULT_INPUT_DIR = os.getenv("EOI_ANALYZER_INPUT_DIR", "eois")
DEFAULT_OUTPUT_DIR = os.getenv("EOI_ANALYZER_OUTPUT_DIR", "outputs")
PROMPT_DIR = os.getenv("EOI_ANALYZER_PROMPT_DIR")

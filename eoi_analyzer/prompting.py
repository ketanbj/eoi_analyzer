from importlib import resources
from pathlib import Path
from string import Template
from typing import Optional

from .config import PROMPT_DIR


class PromptLibrary:
    """
    Load prompt templates from package defaults or a caller-provided override directory.

    Templates use string.Template placeholders, e.g. $document_text, so prompt files can
    contain JSON braces without escaping.
    """

    def __init__(self, prompt_dir: Optional[str] = None):
        self.prompt_dir = Path(prompt_dir or PROMPT_DIR).expanduser() if (prompt_dir or PROMPT_DIR) else None

    def get(self, name: str) -> str:
        if self.prompt_dir:
            override_path = self.prompt_dir / name
            if override_path.exists():
                return override_path.read_text(encoding="utf-8")

        package_root = resources.files("eoi_analyzer")
        return package_root.joinpath("prompts", name).read_text(encoding="utf-8")

    def render(self, name: str, **context) -> str:
        return Template(self.get(name)).safe_substitute(
            {key: "" if value is None else str(value) for key, value in context.items()}
        )

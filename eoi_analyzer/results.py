from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DocumentAnalysis:
    source_path: str
    source_name: str
    text_char_count: int
    engagement_snapshot: str
    recommendation: str
    project_plan: str
    letter_of_intent: Optional[str] = None
    engagement_profile: Optional[Dict[str, Any]] = None
    agent_review: Optional[str] = None
    log: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentFailure:
    source_path: str
    source_name: str
    error: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BatchAnalysis:
    analyses: List[DocumentAnalysis] = field(default_factory=list)
    failures: List[DocumentFailure] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analyses": [analysis.to_dict() for analysis in self.analyses],
            "failures": [failure.to_dict() for failure in self.failures],
        }

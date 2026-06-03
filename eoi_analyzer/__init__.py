from .profile import EngagementProfile
from .results import BatchAnalysis, DocumentAnalysis, DocumentFailure

__all__ = [
    "EOIAnalyzer",
    "EngagementProfile",
    "BatchAnalysis",
    "DocumentAnalysis",
    "DocumentFailure",
]


def __getattr__(name):
    if name == "EOIAnalyzer":
        from .analyzer import EOIAnalyzer

        return EOIAnalyzer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

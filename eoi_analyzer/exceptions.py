# eoi_analyzer/exceptions.py

class EOIAnalyzerError(Exception):
    """Base class for exceptions in this module."""
    pass

class PDFExtractionError(EOIAnalyzerError):
    """Exception raised for errors during PDF extraction."""
    pass
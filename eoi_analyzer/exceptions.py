# eoi_analyzer/exceptions.py

class EOIAnalyzerError(Exception):
    """Base class for exceptions in this module."""
    pass

class PDFExtractionError(EOIAnalyzerError):
    """Exception raised for errors during PDF extraction."""
    pass


class DocumentExtractionError(EOIAnalyzerError):
    """Exception raised for errors during document extraction."""
    pass


class UnsupportedDocumentError(EOIAnalyzerError):
    """Exception raised when a document type is not supported."""
    pass


class EmptyDocumentError(EOIAnalyzerError):
    """Exception raised when a document contains no extractable text."""
    pass

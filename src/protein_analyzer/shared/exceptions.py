"""Custom exceptions for the Protein Analyzer application."""


class ProteinAnalyzerError(Exception):
    """Base exception class for all protein analyzer errors."""

    pass


class FileProcessingError(ProteinAnalyzerError):
    """Exception raised when file processing fails."""

    pass


class APIError(ProteinAnalyzerError):
    """Exception raised when API requests fail."""

    pass


class NCBIError(APIError):
    """Exception raised when NCBI API requests fail."""

    pass


class AlphaFoldError(APIError):
    """Exception raised when AlphaFold API requests fail."""

    pass


class ValidationError(ProteinAnalyzerError):
    """Exception raised when input validation fails."""

    pass


class ConfigurationError(ProteinAnalyzerError):
    """Exception raised when configuration is invalid."""

    pass
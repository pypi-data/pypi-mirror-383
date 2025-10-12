"""Custom exceptions for Databricks Claude CLI."""


class DatabricksClaudeError(Exception):
    """Base exception for Databricks Claude CLI."""

    pass


class AuthenticationError(DatabricksClaudeError):
    """Raised when authentication fails."""

    pass


class ConfigurationError(DatabricksClaudeError):
    """Raised when configuration operations fail."""

    pass


class TokenExpiredError(AuthenticationError):
    """Raised when OAuth token has expired."""

    pass


class CLINotFoundError(ConfigurationError):
    """Raised when required CLI tools are not found."""

    pass

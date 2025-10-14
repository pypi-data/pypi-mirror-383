"""Exception classes for AIAC."""


class AiacError(Exception):
    """Base exception class for all AIAC errors."""
    
    pass


class BackendError(AiacError):
    """Exception raised by backend implementations."""
    
    pass


class ConfigurationError(AiacError):
    """Exception raised for configuration-related issues."""
    
    pass


# Specific error types matching Go implementation
class ErrNoSuchBackend(ConfigurationError):
    """Backend name does not exist in configuration."""
    
    def __init__(self, backend_name: str):
        super().__init__(f"no such backend: {backend_name}")
        self.backend_name = backend_name


class ErrNoDefaultBackend(ConfigurationError):
    """No backend selected and no default configured."""
    
    def __init__(self):
        super().__init__("backend not selected and no default configured")


class ErrNoDefaultModel(ConfigurationError):
    """No model selected and no default configured."""
    
    def __init__(self):
        super().__init__("model not selected and no default configured")


class ErrNoResults(BackendError):
    """LLM provider API returned an empty result."""
    
    def __init__(self):
        super().__init__("no results returned from API")


class ErrUnexpectedStatus(BackendError):
    """LLM provider API returned unexpected status code."""
    
    def __init__(self, status_code: int, message: str = ""):
        msg = f"backend returned unexpected response: {status_code}"
        if message:
            msg += f" - {message}"
        super().__init__(msg)
        self.status_code = status_code


class ErrRequestFailed(BackendError):
    """LLM provider API returned an error for the request."""
    
    def __init__(self, message: str):
        super().__init__(f"request failed: {message}")
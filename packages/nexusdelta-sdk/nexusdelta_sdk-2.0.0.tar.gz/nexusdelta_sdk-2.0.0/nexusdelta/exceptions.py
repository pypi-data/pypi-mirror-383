# Nexus Delta SDK Exceptions

class NexusDeltaError(Exception):
    """Base exception for Nexus Delta SDK"""
    pass

class AuthenticationError(NexusDeltaError):
    """Raised when authentication fails"""
    pass

class AgentError(NexusDeltaError):
    """Raised when agent operations fail"""
    pass

class NetworkError(NexusDeltaError):
    """Raised when network operations fail"""
    pass

class ValidationError(NexusDeltaError):
    """Raised when data validation fails"""
    pass

class ServiceUnavailableError(NexusDeltaError):
    """Raised when services are unavailable"""
    pass
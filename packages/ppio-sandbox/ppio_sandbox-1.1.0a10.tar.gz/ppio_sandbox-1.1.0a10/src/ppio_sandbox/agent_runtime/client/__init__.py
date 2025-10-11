"""
PPIO Agent Runtime Client Module

Provides client functionality for AI Agents, targeted at backend developers
"""

# Main client class
from .client import AgentRuntimeClient

# Session management
from .session import SandboxSession

# Authentication and template management
from .auth import AuthManager
from .template import TemplateManager

# Data models
from .models import (
    AgentTemplate,
    ClientConfig,
    InvocationRequest,
    InvocationResponse,
    SandboxConfig,
    SessionStatus,
    # PingResponse imported from runtime module
    PingResponse,
    PingStatus,
)

# Exception classes
from .exceptions import (
    AgentClientError,
    AuthenticationError,
    InvocationError,
    NetworkError,
    QuotaExceededError,
    RateLimitError,
    SandboxCreationError,
    SandboxOperationError,
    SessionNotFoundError,
    TemplateNotFoundError,
)

__version__ = "1.0.0"

__all__ = [
    # Core client classes
    "AgentRuntimeClient",
    "SandboxSession",
    "AuthManager", 
    "TemplateManager",
    
    # Data models
    "AgentTemplate",
    "ClientConfig",
    "InvocationRequest",
    "InvocationResponse",
    "PingResponse",
    "PingStatus",
    "SandboxConfig",
    "SessionStatus",
    
    # Exception classes
    "AgentClientError",
    "AuthenticationError",
    "InvocationError",
    "NetworkError",
    "QuotaExceededError",
    "RateLimitError",
    "SandboxCreationError",
    "SandboxOperationError",
    "SessionNotFoundError",
    "TemplateNotFoundError",
]
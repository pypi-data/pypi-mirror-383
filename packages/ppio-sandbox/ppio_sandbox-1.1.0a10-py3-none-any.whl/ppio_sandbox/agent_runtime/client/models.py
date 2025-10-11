"""
Agent Runtime Client Data Models

Defines data models used by the client
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Import shared PingResponse model
from ..runtime.models import PingResponse, PingStatus


class SessionStatus(str, Enum):
    """Session status"""
    ACTIVE = "active"      # Running, can process requests
    PAUSED = "paused"      # Paused, retains state but does not process requests
    INACTIVE = "inactive"  # Inactive state
    CLOSED = "closed"      # Closed, resources released
    ERROR = "error"        # Error state


class AgentTemplate(BaseModel):
    """Agent template information"""
    template_id: str
    name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    status: str
    
    # Agent metadata (core field)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    """
    Agent metadata, contains complete AgentConfig data structure, consistent with CLI tool configuration file format.
    
    Typical structure example (following Kubernetes-style YAML configuration format):
    {
      "agent": {
        "apiVersion": "v1",
        "kind": "Agent",
        "metadata": {
          "name": "string",              // Agent name
          "version": "string",           // Agent version
          "author": "string",            // Author email (required)
          "description": "string",       // Agent description
          "created": "string"            // Creation time (ISO 8601 format)
        },
        "spec": {
          "entrypoint": "string",        // Python entry file, e.g. "agent.py" (must be .py file)
          "runtime": {
            "timeout": "number",         // Startup timeout in seconds, converted to readyCmd timeout parameter (1-3600)
            "memory_limit": "string",    // Memory limit, converted to memoryMb (supports formats like "512Mi", "1Gi")
            "cpu_limit": "string"        // CPU limit, converted to cpuCount (supports formats like "1", "1000m")
          },
          "sandbox": {
            "template_id": "string"      // Template ID after deployment
          }
        },
        // Status fields - used to track deployment and build status (maintained by system, users should not modify manually)
        "status": {
          "phase": "string",            // Current deployment phase
          "template_id": "string",      // Actual template ID after successful build (for subsequent updates)
          "last_deployed": "string",    // Last deployment time
          "build_id": "string"          // Unique identifier for deployment
        }
      }
    }
    """
    
    # Extended fields
    size: Optional[int] = None  # Template size (bytes)
    build_time: Optional[float] = None  # Build time (seconds)
    dependencies: List[str] = Field(default_factory=list)
    runtime_info: Optional[Dict[str, Any]] = None


class SandboxConfig(BaseModel):
    """Sandbox configuration"""
    timeout_seconds: int = 300
    memory_limit: Optional[str] = None  # e.g. "512Mi", "1Gi"
    cpu_limit: Optional[str] = None     # e.g. "500m", "1"
    env_vars: Optional[Dict[str, str]] = Field(default_factory=dict)
    volumes: List[Dict[str, str]] = Field(default_factory=list)
    ports: List[int] = Field(default_factory=lambda: [8080])
    startup_cmd: Optional[str] = None


class ClientConfig(BaseModel):
    """Client configuration"""
    base_url: str = "https://api.sandbox.ppio.cn"  # Default API endpoint
    timeout: int = 300
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Connection pool configuration
    max_connections: int = 100
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 30.0


class InvocationRequest(BaseModel):
    """Enhanced invocation request model"""
    # Basic fields - using correct field names
    input: Optional[str] = None  # Field name expected by Agent service
    prompt: Optional[str] = None  # Backward compatibility
    data: Optional[Dict[str, Any]] = None
    sandbox_id: Optional[str] = None  # Optional, usually auto-filled by system
    
    # Control fields
    timeout: Optional[int] = None
    stream: bool = False
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    
    # Streaming control
    stream_options: Optional[Dict[str, Any]] = None
    
    # Backward compatible property
    @property
    def session_id(self) -> Optional[str]:
        """Session ID (equivalent to sandbox_id, backward compatibility)"""
        return self.sandbox_id


class InvocationResponse(BaseModel):
    """Enhanced invocation response model"""
    result: Any
    status: str = "success"
    duration: float
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    
    # Performance information
    processing_time: Optional[float] = None
    queue_time: Optional[float] = None
    
    # Usage statistics
    tokens_used: Optional[int] = None
    cost: Optional[float] = None


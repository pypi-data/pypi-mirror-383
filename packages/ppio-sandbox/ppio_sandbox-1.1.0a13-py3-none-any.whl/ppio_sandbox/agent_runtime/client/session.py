"""
Sandbox Session Management

Manages the lifecycle of a single Sandbox instance and Agent invocations
"""

from datetime import datetime
from typing import Any, AsyncIterator, Dict, Optional, Union
import httpx
from ppio_sandbox.core import AsyncSandbox

from .exceptions import (
    InvocationError, 
    NetworkError, 
    SandboxOperationError, 
    SessionNotFoundError
)
from .models import InvocationRequest, PingResponse, PingStatus, SessionStatus


class SandboxSession:
    """Sandbox session management"""
    
    def __init__(
        self,
        template_id: str,
        sandbox: AsyncSandbox,  # PPIO Sandbox instance
        client: "AgentRuntimeClient"
    ):
        """Initialize session
        
        Args:
            template_id: Template ID
            sandbox: PPIO Sandbox instance (one-to-one relationship)
            client: Agent Runtime client reference
        """
        self.template_id = template_id
        self.sandbox = sandbox
        self._client_ref = client  # Avoid circular reference
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.status = SessionStatus.ACTIVE
        self._host_url: Optional[str] = None
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get HTTP client"""
        if self._http_client is None:
            # Get authentication headers from client reference
            auth_headers = self._client_ref.auth_manager.get_auth_headers()
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers=auth_headers  # Use complete authentication headers, including Authorization
            )
        return self._http_client
    
    async def _close_http_client(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    # === Core Invocation Methods ===
    async def invoke(
        self,
        request: Union[InvocationRequest, Dict[str, Any], str],
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncIterator[str]]:
        """Invoke Agent
        
        Args:
            request: Invocation request (supports multiple formats)
            stream: Whether to use streaming response
            
        Returns:
            Response object or streaming iterator
            
        Raises:
            InvocationError: Raised when invocation fails
            SessionNotFoundError: Raised when session does not exist
            NetworkError: Raised on network error
        """
        if self.status not in [SessionStatus.ACTIVE]:
            raise SessionNotFoundError(f"Session {self.sandbox_id} is not active (status: {self.status})")
        
        # Normalize request format
        if isinstance(request, str):
            request_data = InvocationRequest(input=request, stream=stream)  # Use correct field name
        elif isinstance(request, dict):
            request_data = InvocationRequest(**request)
            if stream is not None:
                request_data.stream = stream
        elif isinstance(request, InvocationRequest):
            request_data = request
            if stream is not None:
                request_data.stream = stream
        else:
            raise InvocationError("Invalid request format")
        
        # Set sandbox_id (if not already set)
        if not request_data.sandbox_id:
            request_data.sandbox_id = self.sandbox_id
        
        try:
            self.last_activity = datetime.now()
            
            if request_data.stream:
                return self._invoke_stream(request_data)
            else:
                return await self._invoke_sync(request_data)
                
        except Exception as e:
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                raise NetworkError(f"Network error during invocation: {str(e)}")
            else:
                raise InvocationError(f"Agent invocation failed: {str(e)}")
    
    async def _invoke_sync(self, request: InvocationRequest) -> Dict[str, Any]:
        """Synchronous Agent invocation"""
        client = await self._get_http_client()
        
        request_url = f"{self.host_url}/invocations"
        
        # Simplify request body, only send fields needed by Agent service
        request_body = {}
        if request.input:
            request_body["prompt"] = request.input
        elif request.prompt:  # Backward compatibility
            request_body["prompt"] = request.prompt
        
        response = await client.post(
            request_url,
            json=request_body,
            timeout=httpx.Timeout(request.timeout or 300)
        )
        
        if response.status_code != 200:
            raise InvocationError(f"Agent returned status {response.status_code} from URL [{request_url}]: {response.text}")
        
        return response.json()
    
    async def _invoke_stream(self, request: InvocationRequest) -> AsyncIterator[str]:
        """Streaming Agent invocation"""
        client = await self._get_http_client()
        
        # Simplify request body, only send fields needed by Agent service
        request_body = {}
        if request.input:
            request_body["prompt"] = request.input
        elif request.prompt:  # Backward compatibility
            request_body["prompt"] = request.prompt
        
        async with client.stream(
            "POST",
            f"{self.host_url}/invocations",
            json=request_body,
            timeout=httpx.Timeout(request.timeout or 300)
        ) as response:
            if response.status_code != 200:
                content = await response.aread()
                request_url = f"{self.host_url}/invocations"
                raise InvocationError(f"Agent returned status {response.status_code} from URL [{request_url}]: {content}")
            
            async for chunk in response.aiter_text():
                if chunk.strip():  # Skip empty lines
                    yield chunk
    
    # === Sandbox Lifecycle Management ===
    async def pause(self) -> None:
        """Pause Sandbox instance
        
        After pausing:
        - Sandbox enters sleep state, retains memory state
        - Stops CPU computation, saves resources
        - Can resume execution via resume()
        
        Raises:
            SandboxOperationError: Raised when pause fails
        """
        try:
            if hasattr(self.sandbox, 'pause'):
                await self.sandbox.pause()
            else:
                # If sandbox doesn't have pause method, use API call
                await self._call_sandbox_api("pause")
            
            self.status = SessionStatus.PAUSED
            
        except Exception as e:
            raise SandboxOperationError(f"Failed to pause sandbox: {str(e)}")
    
    async def resume(self) -> None:
        """Resume Sandbox instance
        
        After resuming:
        - Sandbox recovers from paused state
        - Maintains previous memory state and context
        - Can continue processing requests
        
        Raises:
            SandboxOperationError: Raised when resume fails
        """
        try:
            if hasattr(self.sandbox, 'resume'):
                await self.sandbox.resume()
            else:
                # If sandbox doesn't have resume method, use API call
                await self._call_sandbox_api("resume")
            
            self.status = SessionStatus.ACTIVE
            
        except Exception as e:
            raise SandboxOperationError(f"Failed to resume sandbox: {str(e)}")
    
    async def _call_sandbox_api(self, action: str) -> None:
        """Call Sandbox API to execute operation"""
        # This needs to be implemented based on actual Sandbox API
        # Using mock implementation for now
        pass
    
    # === Session Management ===
    async def ping(self) -> PingResponse:
        """Health check
        
        Returns:
            Health check response
            
        Raises:
            NetworkError: Raised on network error
            InvocationError: Raised when check fails
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(
                f"{self.host_url}/ping",
                timeout=httpx.Timeout(10.0)
            )
            
            if response.status_code == 200:
                data = response.json()
                return PingResponse(
                    status=data.get("status", "healthy"),
                    message=data.get("message"),
                    timestamp=data.get("timestamp", datetime.now().isoformat())
                )
            else:
                return PingResponse(
                    status=PingStatus.HEALTHY_BUSY,  # Use enum value to represent error state
                    message=f"HTTP {response.status_code}: {response.text}",
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                raise NetworkError(f"Network error during ping: {str(e)}")
            else:
                raise InvocationError(f"Ping failed: {str(e)}")
    
    async def get_status(self) -> SessionStatus:
        """Get session status
        
        Returns:
            Session status (ACTIVE, PAUSED, INACTIVE, CLOSED, ERROR)
        """
        # Can add actual status check logic
        try:
            # Try ping to confirm status
            ping_response = await self.ping()
            # Support multiple healthy status formats (case insensitive)
            healthy_statuses = ["healthy", "Healthy", "HealthyBusy", "healthybusy"]
            if ping_response.status in healthy_statuses:
                if self.status == SessionStatus.PAUSED:
                    return SessionStatus.PAUSED
                else:
                    return SessionStatus.ACTIVE
            else:
                return SessionStatus.ERROR
        except Exception:
            return SessionStatus.ERROR
    
    async def refresh(self) -> None:
        """Refresh session (reset timeout)"""
        self.last_activity = datetime.now()
        # Can add actual refresh logic, such as sending keepalive signal to Sandbox
    
    async def close(self) -> None:
        """Close session and destroy Sandbox
        
        Execution steps:
        1. Stop Agent service
        2. Destroy Sandbox instance
        3. Release all resources
        4. Update session status to CLOSED
        """
        try:
            # Close HTTP client
            await self._close_http_client()
            
            # Destroy Sandbox instance
            if hasattr(self.sandbox, 'close'):
                await self.sandbox.close()
            elif hasattr(self.sandbox, 'kill'):
                await self.sandbox.kill()
            
            self.status = SessionStatus.CLOSED
            
        except Exception as e:
            self.status = SessionStatus.ERROR
            raise SandboxOperationError(f"Failed to close session: {str(e)}")
    
    # === Properties ===
    @property
    def host_url(self) -> str:
        """Get Sandbox host URL"""
        if not self._host_url:
            if self.sandbox and hasattr(self.sandbox, 'get_host'):
                # Use actual Sandbox API
                host = self.sandbox.get_host(8080)
                self._host_url = f"https://{host}"
            else:
                # Mock URL (for testing)
                self._host_url = f"https://session-{self.sandbox_id}.ppio.sandbox"
        return self._host_url
    
    @property
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status == SessionStatus.ACTIVE
    
    @property
    def is_paused(self) -> bool:
        """Check if session is paused"""
        return self.status == SessionStatus.PAUSED
    
    @property
    def sandbox_id(self) -> str:
        """Get Sandbox instance ID (also session ID)"""
        if hasattr(self.sandbox, 'id'):
            return self.sandbox.id
        elif hasattr(self.sandbox, 'sandbox_id'):
            return self.sandbox.sandbox_id
        else:
            return f"sandbox-{id(self.sandbox)}"
    
    @property
    def session_id(self) -> str:
        """Get session ID (equivalent to sandbox_id)"""
        return self.sandbox_id
    
    @property
    def age_seconds(self) -> float:
        """Get session age in seconds"""
        return (datetime.now() - self.created_at).total_seconds()
    
    @property
    def idle_seconds(self) -> float:
        """Get session idle time in seconds"""
        return (datetime.now() - self.last_activity).total_seconds()
    
    def __repr__(self) -> str:
        return f"SandboxSession(id={self.sandbox_id}, status={self.status}, template={self.template_id})"
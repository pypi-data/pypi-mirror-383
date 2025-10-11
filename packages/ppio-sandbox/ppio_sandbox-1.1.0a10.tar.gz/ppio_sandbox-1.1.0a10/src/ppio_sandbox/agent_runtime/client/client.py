"""
Agent Runtime Client

Client for backend developers to manage Sandbox sessions and Agent invocations
"""

import asyncio
import os
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from ppio_sandbox.core import AsyncSandbox  # 导入现有的异步 Sandbox 功能
from .auth import AuthManager
from .exceptions import (
    AuthenticationError,
    InvocationError,
    SessionNotFoundError,
    SandboxCreationError,
    TemplateNotFoundError
)
from .models import (
    AgentTemplate,
    ClientConfig,
    InvocationRequest,
    InvocationResponse,
    SandboxConfig
)
from .session import SandboxSession
from .template import TemplateManager


class AgentRuntimeClient:
    """Agent Runtime Client"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 300,
        config: Optional[ClientConfig] = None
    ):
        """Initialize the client
        
        Args:
            api_key: API key, if not provided it will be read from environment variable PPIO_API_KEY
            base_url: Sandbox platform base URL, if not provided the default value will be used
            timeout: Default timeout in seconds
            config: Client configuration
            
        Environment Variables:
            PPIO_API_KEY: API key
            
        Raises:
            AuthenticationError: Raised when API Key is not provided and environment variable does not exist
        """
        # Set configuration
        if config:
            self.config = config
        else:
            # If config is not provided, create a new configuration
            if base_url:
                self.config = ClientConfig(base_url=base_url, timeout=timeout)
            else:
                # Use default configuration
                self.config = ClientConfig(timeout=timeout)
        
        # Initialize authentication manager
        self.auth_manager = AuthManager(api_key)
        
        # Initialize template manager (only pass auth_manager)
        self.template_manager = TemplateManager(self.auth_manager)
        
        # Session management
        self._sessions: Dict[str, SandboxSession] = {}
        self._closed = False
    
    # === Session Management ===
    async def create_session(
        self,
        template_id: str,
        timeout_seconds: int = 300,
        config: Optional[SandboxConfig] = None,
    ) -> SandboxSession:
        """Create a new Sandbox session
        
        Each call will:
        1. Create a new Sandbox instance from the template
        2. Start the Agent service in the Sandbox
        3. Return the corresponding SandboxSession object
        
        Args:
            template_id: Agent template ID
            timeout_seconds: Session timeout in seconds
            config: Sandbox configuration
            env_vars: Environment variables
        Returns:
            SandboxSession object
            
        Raises:
            SandboxCreationError: Raised when creation fails
            AuthenticationError: Raised when authentication fails
            TemplateNotFoundError: Raised when template does not exist
        """
        if self._closed:
            raise RuntimeError("Client is closed")
        
        try:
            # Verify template exists
            if not await self.template_manager.template_exists(template_id):
                raise TemplateNotFoundError(f"Template {template_id} not found")
            
            # Prepare Sandbox configuration
            sandbox_config = config or SandboxConfig()
            
            # Create Sandbox instance
            # This needs to be adjusted based on actual Sandbox API
            sandbox = await self._create_sandbox_instance(
                template_id=template_id,
                timeout_seconds=timeout_seconds,
                config=sandbox_config,
            )
            
            # Create session
            session = SandboxSession(
                template_id=template_id,
                sandbox=sandbox,
                client=self
            )
            
            # Register session
            self._sessions[session.sandbox_id] = session
            
            return session
            
        except TemplateNotFoundError:
            raise
        except AuthenticationError:
            raise
        except Exception as e:
            raise SandboxCreationError(f"Failed to create sandbox session: {str(e)}")
    
    async def _create_sandbox_instance(
        self,
        template_id: str,
        timeout_seconds: int,
        config: SandboxConfig,
    ) -> AsyncSandbox:
        """Create Sandbox instance"""
        try:
            sandbox = await AsyncSandbox.create(
                template=template_id,
                timeout=timeout_seconds,
                metadata={"created_by": "agent_runtime_client"},
                envs=config.env_vars,
                api_key=self.auth_manager.api_key,
                # Secure mode, default is True
                secure=True,
                # Auto-pause setting
                auto_pause=False
            )

            if config.startup_cmd:
                await sandbox.commands.run(config.startup_cmd)
            
            return sandbox
            
        except Exception as e:
            raise SandboxCreationError(f"Failed to create sandbox instance: {str(e)}")
    
    async def get_session(self, sandbox_id: str) -> Optional[SandboxSession]:
        """Get existing session
        
        Args:
            sandbox_id: Sandbox/session ID
            
        Returns:
            Session object, or None if not found
        """
        return self._sessions.get(sandbox_id)
    
    async def list_sessions(self) -> List[SandboxSession]:
        """List all active sessions
        
        Returns:
            List of sessions
        """
        return list(self._sessions.values())
    
    async def close_session(self, sandbox_id: str) -> None:
        """Close specified session
        
        Args:
            sandbox_id: Sandbox/session ID
            
        Raises:
            SessionNotFoundError: Raised when session does not exist
        """
        session = self._sessions.get(sandbox_id)
        if not session:
            raise SessionNotFoundError(f"Session {sandbox_id} not found")
        
        try:
            await session.close()
        finally:
            # Remove from session list
            self._sessions.pop(sandbox_id, None)
    
    async def close_all_sessions(self) -> None:
        """Close all sessions"""
        sessions = list(self._sessions.values())
        self._sessions.clear()
        
        # Close all sessions concurrently
        if sessions:
            await asyncio.gather(
                *[session.close() for session in sessions],
                return_exceptions=True
            )
    
    # === Template Management ===
    async def list_templates(
        self, 
        tags: Optional[List[str]] = None,
        name_filter: Optional[str] = None
    ) -> List[AgentTemplate]:
        """List available Agent templates
        
        Args:
            tags: Tag filter
            name_filter: Name filter
        
        Returns:
            List of templates
        """
        return await self.template_manager.list_templates(tags, name_filter)
    
    async def get_template(self, template_id: str) -> AgentTemplate:
        """Get specific template information
        
        Args:
            template_id: Template ID
            
        Returns:
            Template object
            
        Raises:
            TemplateNotFoundError: Raised when template does not exist
        """
        return await self.template_manager.get_template(template_id)
    
    # === Convenient Invocation Methods ===
    async def invoke_agent(
        self,
        template_id: str,
        request: Union[InvocationRequest, Dict[str, Any], str],
        create_session: bool = True,
        sandbox_id: Optional[str] = None,
        timeout: Optional[int] = None,
        env_vars: Optional[Dict[str, Any]] = None,
        startup_cmd: Optional[str] = None,
    ) -> InvocationResponse:
        """Convenient method: Invoke Agent directly (auto-manage session)
        
        Args:
            template_id: Template ID
            request: Invocation request (supports multiple formats)
            create_session: Whether to automatically create a new session
            sandbox_id: Specified Sandbox/session ID to use
            timeout: Invocation timeout in seconds
            env_vars: Environment variables
            
        Returns:
            Invocation response
            
        Raises:
            SessionNotFoundError: Raised when specified session does not exist
            InvocationError: Raised when invocation fails
        """
        import time
        start_time = time.time()
        
        # Get or create session
        if sandbox_id:
            session = await self.get_session(sandbox_id)
            if not session:
                raise SessionNotFoundError(f"Session {sandbox_id} not found")
        elif create_session:
            # Build configuration, only pass env_vars when it has a value
            config_kwargs = {}
            if env_vars:
                config_kwargs['env_vars'] = env_vars
            if startup_cmd:
                config_kwargs['startup_cmd'] = startup_cmd
            session = await self.create_session(
                template_id, 
                timeout or self.config.timeout, 
                config=SandboxConfig(**config_kwargs)
            )
        else:
            raise ValueError("Either sandbox_id or create_session=True must be provided")
        
        try:
            # Invoke Agent
            result = await session.invoke(request)
            
            # Construct response
            return InvocationResponse(
                result=result,
                status="success",
                duration=time.time() - start_time,
                metadata={
                    "sandbox_id": session.sandbox_id,
                    "template_id": template_id
                }
            )
            
        except Exception as e:
            return InvocationResponse(
                result=None,
                status="error",
                duration=time.time() - start_time,
                error=str(e),
                error_type=type(e).__name__,
                metadata={
                    "sandbox_id": session.sandbox_id if 'session' in locals() else None,
                    "template_id": template_id
                }
            )
        finally:
            # If session was auto-created, close it after invocation completes
            if create_session and not sandbox_id and 'session' in locals():
                try:
                    await session.close()
                    self._sessions.pop(session.sandbox_id, None)
                except Exception:
                    pass  # Ignore close errors
    
    async def invoke_agent_stream(
        self,
        template_id: str,
        request: Union[InvocationRequest, Dict[str, Any], str],
        create_session: bool = True,
        sandbox_id: Optional[str] = None,
        env_vars: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Convenient method: Stream invoke Agent
        
        Args:
            template_id: Template ID
            request: Invocation request
            create_session: Whether to automatically create a new session
            sandbox_id: Specified Sandbox/session ID to use
            env_vars: Environment variables
        Yields:
            Streaming response data
        """
        # Get or create session
        if sandbox_id:
            session = await self.get_session(sandbox_id)
            if not session:
                raise SessionNotFoundError(f"Session {sandbox_id} not found")
        elif create_session:
            # Build configuration, only pass env_vars when it has a value
            config_kwargs = {}
            if env_vars:
                config_kwargs['env_vars'] = env_vars
            session = await self.create_session(
                template_id, 
                config=SandboxConfig(**config_kwargs)
            )
        else:
            raise ValueError("Either sandbox_id or create_session=True must be provided")
        
        try:
            # Stream invocation
            async for chunk in await session.invoke(request, stream=True):
                yield chunk
                
        finally:
            # If session was auto-created, close it after invocation completes
            if create_session and not sandbox_id:
                try:
                    await session.close()
                    self._sessions.pop(session.sandbox_id, None)
                except Exception:
                    pass  # Ignore close errors
    
    # === Context Manager Support ===
    async def __aenter__(self) -> "AgentRuntimeClient":
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.close()
    
    async def close(self) -> None:
        """Close client and clean up resources"""
        if self._closed:
            return
        
        self._closed = True
        
        # Close all sessions
        await self.close_all_sessions()
        
        # Close template manager
        await self.template_manager.close()
    
    def __repr__(self) -> str:
        return f"AgentRuntimeClient(sessions={len(self._sessions)}, closed={self._closed})"
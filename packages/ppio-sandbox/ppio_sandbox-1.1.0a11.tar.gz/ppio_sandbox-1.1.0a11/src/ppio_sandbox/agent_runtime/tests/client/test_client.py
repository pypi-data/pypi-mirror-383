"""
AgentRuntimeClient unit tests

Tests client main class functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from ppio_sandbox.agent_runtime.client.client import AgentRuntimeClient
from ppio_sandbox.agent_runtime.client.auth import AuthManager
from ppio_sandbox.agent_runtime.client.models import (
    ClientConfig,
    SandboxConfig,
    InvocationRequest,
    InvocationResponse,
    SessionStatus
)
from ppio_sandbox.agent_runtime.client.exceptions import (
    AuthenticationError,
    SandboxCreationError,
    SessionNotFoundError,
    TemplateNotFoundError,
    InvocationError
)

from .mock_sandbox import MockAsyncSandbox
from .test_fixtures import create_sample_template


class TestAgentRuntimeClientInit:
    """AgentRuntimeClient initialization tests"""
    
    @pytest.mark.unit
    def test_client_init_with_api_key(self, test_api_key: str):
        """Test initialization with API Key"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        assert client.auth_manager.api_key == test_api_key
        assert isinstance(client.config, ClientConfig)
        assert client.template_manager is not None
        assert client._sessions == {}
        assert client._closed is False
    
    @pytest.mark.unit
    def test_client_init_with_config(self, test_api_key: str, client_config: ClientConfig):
        """Test initialization with configuration"""
        client = AgentRuntimeClient(
            api_key=test_api_key,
            config=client_config
        )
        
        assert client.config is client_config
        assert client.config.base_url == "https://api.test.ppio.ai"
        assert client.config.timeout == 30
    
    @pytest.mark.unit
    def test_client_init_with_base_url(self, test_api_key: str):
        """Test initialization with base URL"""
        base_url = "https://custom.api.com"
        client = AgentRuntimeClient(
            api_key=test_api_key,
            base_url=base_url
        )
        
        assert client.config.base_url == base_url
    
    @pytest.mark.unit
    def test_client_init_from_env(self, test_api_key: str):
        """Test initialization from environment variables"""
        with patch.dict('os.environ', {'PPIO_API_KEY': test_api_key}):
            client = AgentRuntimeClient()
            assert client.auth_manager.api_key == test_api_key
    
    @pytest.mark.unit
    def test_client_init_without_api_key(self):
        """Test initialization fails without API Key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(AuthenticationError):
                AgentRuntimeClient()


class TestAgentRuntimeClientSessionManagement:
    """AgentRuntimeClient session management tests"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_session_success(self, test_api_key: str, sample_template):
        """Test successful session creation"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        # Mock template_manager
        with patch.object(client.template_manager, 'template_exists', return_value=True):
            with patch.object(client, '_create_sandbox_instance') as mock_create:
                mock_sandbox = MockAsyncSandbox()
                mock_create.return_value = mock_sandbox
                
                session = await client.create_session(sample_template.template_id)
        
        assert session.template_id == sample_template.template_id
        assert session.sandbox is mock_sandbox
        assert session.sandbox_id in client._sessions
        assert client._sessions[session.sandbox_id] is session
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_create_session_template_not_found(self, test_api_key: str):
        """Test session creation fails when template doesn't exist"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with patch.object(client.template_manager, 'template_exists', return_value=False):
            with pytest.raises(TemplateNotFoundError) as exc_info:
                await client.create_session("non-existent-template")
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_create_session_sandbox_creation_error(self, test_api_key: str, sample_template):
        """Test Sandbox creation failure"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with patch.object(client.template_manager, 'template_exists', return_value=True):
            with patch.object(client, '_create_sandbox_instance', side_effect=Exception("Creation failed")):
                with pytest.raises(SandboxCreationError) as exc_info:
                    await client.create_session(sample_template.template_id)
        
        assert "Failed to create sandbox session" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_create_session_closed_client(self, test_api_key: str, sample_template):
        """Test closed client session creation"""
        client = AgentRuntimeClient(api_key=test_api_key)
        client._closed = True
        
        with pytest.raises(RuntimeError) as exc_info:
            await client.create_session(sample_template.template_id)
        
        assert "Client is closed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_get_session_existing(self, mock_sandbox_session):
        """Test getting existing session"""
        client = AgentRuntimeClient(api_key="test-key")
        client._sessions[mock_sandbox_session.sandbox_id] = mock_sandbox_session
        
        session = await client.get_session(mock_sandbox_session.sandbox_id)
        
        assert session is mock_sandbox_session
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_get_session_not_found(self, test_api_key: str):
        """Test getting non-existent session"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        session = await client.get_session("non-existent-session")
        
        assert session is None
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_list_sessions(self, test_api_key: str, mock_sandbox_session):
        """Test listing sessions"""
        client = AgentRuntimeClient(api_key=test_api_key)
        client._sessions[mock_sandbox_session.sandbox_id] = mock_sandbox_session
        
        sessions = await client.list_sessions()
        
        assert len(sessions) == 1
        assert sessions[0] is mock_sandbox_session
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_close_session_success(self, test_api_key: str, mock_sandbox_session):
        """Test successful session closing"""
        client = AgentRuntimeClient(api_key=test_api_key)
        client._sessions[mock_sandbox_session.sandbox_id] = mock_sandbox_session
        
        await client.close_session(mock_sandbox_session.sandbox_id)
        
        assert mock_sandbox_session.sandbox_id not in client._sessions
        mock_sandbox_session.close.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_close_session_not_found(self, test_api_key: str):
        """Test closing non-existent session"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with pytest.raises(SessionNotFoundError) as exc_info:
            await client.close_session("non-existent-session")
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_close_all_sessions(self, test_api_key: str):
        """Test closing all sessions"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        # Create multiple mock sessions
        sessions = []
        for i in range(3):
            session = Mock()
            session.sandbox_id = f"session-{i}"
            session.close = AsyncMock()
            client._sessions[session.sandbox_id] = session
            sessions.append(session)
        
        await client.close_all_sessions()
        
        assert len(client._sessions) == 0
        for session in sessions:
            session.close.assert_called_once()


class TestAgentRuntimeClientTemplateManagement:
    """AgentRuntimeClient template management tests"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_list_templates(self, test_api_key: str, sample_templates):
        """Test listing templates"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with patch.object(client.template_manager, 'list_templates') as mock_list:
            mock_list.return_value = sample_templates
            templates = await client.list_templates()
        
        assert templates is sample_templates
        mock_list.assert_called_once_with(None, None)
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_list_templates_with_filters(self, test_api_key: str, sample_templates):
        """Test listing templates with filters"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with patch.object(client.template_manager, 'list_templates') as mock_list:
            mock_list.return_value = sample_templates
            await client.list_templates(tags=["ai"], name_filter="test")
        
        mock_list.assert_called_once_with(["ai"], "test")
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_get_template(self, test_api_key: str, sample_template):
        """Test getting template"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with patch.object(client.template_manager, 'get_template') as mock_get:
            mock_get.return_value = sample_template
            template = await client.get_template(sample_template.template_id)
        
        assert template is sample_template
        mock_get.assert_called_once_with(sample_template.template_id)


class TestAgentRuntimeClientConvenienceMethods:
    """AgentRuntimeClient convenience method tests"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_invoke_agent_create_session(self, test_api_key: str, sample_template):
        """Test Agent invocation with automatic session creation"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        # Mock session creation
        mock_session = Mock()
        mock_session.sandbox_id = "auto-session"
        mock_session.invoke = AsyncMock(return_value={"result": "success"})
        mock_session.close = AsyncMock()
        
        with patch.object(client, 'create_session', return_value=mock_session):
            response = await client.invoke_agent(
                template_id=sample_template.template_id,
                request="test prompt"
            )
        
        assert isinstance(response, InvocationResponse)
        assert response.result["result"] == "success"
        assert response.status == "success"
        assert response.duration >= 0
        
        # Verify session was automatically closed
        mock_session.close.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_invoke_agent_existing_session(self, test_api_key: str, mock_sandbox_session):
        """Test Agent invocation using existing session"""
        client = AgentRuntimeClient(api_key=test_api_key)
        client._sessions[mock_sandbox_session.sandbox_id] = mock_sandbox_session
        
        with patch.object(client, 'get_session', return_value=mock_sandbox_session):
            response = await client.invoke_agent(
                template_id="any-template",
                request="test prompt",
                create_session=False,
                sandbox_id=mock_sandbox_session.sandbox_id
            )
        
        assert isinstance(response, InvocationResponse)
        mock_sandbox_session.invoke.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_invoke_agent_session_not_found(self, test_api_key: str):
        """Test Agent invocation when session doesn't exist"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with patch.object(client, 'get_session', return_value=None):
            with pytest.raises(SessionNotFoundError):
                await client.invoke_agent(
                    template_id="any-template",
                    request="test prompt",
                    create_session=False,
                    sandbox_id="non-existent"
                )
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_invoke_agent_error_handling(self, test_api_key: str, sample_template):
        """Test Agent invocation error handling"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        # Mock session invocation failure
        mock_session = Mock()
        mock_session.sandbox_id = "error-session"
        mock_session.invoke = AsyncMock(side_effect=Exception("Invocation failed"))
        mock_session.close = AsyncMock()
        
        with patch.object(client, 'create_session', return_value=mock_session):
            response = await client.invoke_agent(
                template_id=sample_template.template_id,
                request="test prompt"
            )
        
        assert response.status == "error"
        assert "Invocation failed" in response.error
        assert response.error_type == "Exception"
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_invoke_agent_stream(self, test_api_key: str, sample_template):
        """Test streaming Agent invocation"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        # Mock streaming response
        async def mock_stream():
            for chunk in ["chunk1", "chunk2", "chunk3"]:
                yield chunk
        
        mock_session = Mock()
        mock_session.sandbox_id = "stream-session"
        mock_session.invoke = AsyncMock(return_value=mock_stream())
        mock_session.close = AsyncMock()
        
        with patch.object(client, 'create_session', return_value=mock_session):
            chunks = []
            async for chunk in client.invoke_agent_stream(
                template_id=sample_template.template_id,
                request="test prompt"
            ):
                chunks.append(chunk)
        
        assert chunks == ["chunk1", "chunk2", "chunk3"]
        mock_session.close.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_invoke_agent_invalid_parameters(self, test_api_key: str):
        """Test Agent invocation with invalid parameters"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with pytest.raises(ValueError) as exc_info:
            await client.invoke_agent(
                template_id="any-template",
                request="test prompt",
                create_session=False,  # Don't create session
                sandbox_id=None        # And don't provide session ID
            )
        
        assert "Either sandbox_id or create_session=True must be provided" in str(exc_info.value)


class TestAgentRuntimeClientContextManager:
    """AgentRuntimeClient context manager tests"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_async_context_manager(self, test_api_key: str):
        """Test async context manager"""
        async with AgentRuntimeClient(api_key=test_api_key) as client:
            assert not client._closed
            assert isinstance(client, AgentRuntimeClient)
        
        # Should be closed after exit
        assert client._closed
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_close_method(self, test_api_key: str):
        """Test close method"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        # Add some sessions
        mock_session = Mock()
        mock_session.close = AsyncMock()
        client._sessions["test-session"] = mock_session
        
        await client.close()
        
        assert client._closed is True
        assert len(client._sessions) == 0
        mock_session.close.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_close_idempotent(self, test_api_key: str):
        """Test repeated closing"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        await client.close()
        assert client._closed is True
        
        # Closing again should be fine
        await client.close()
        assert client._closed is True


class TestAgentRuntimeClientSandboxCreation:
    """AgentRuntimeClient Sandbox creation tests"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    
    async def test_create_sandbox_instance_success(self, test_api_key: str, sandbox_config: SandboxConfig):
        """Test successful Sandbox instance creation"""
        client = AgentRuntimeClient(api_key=test_api_key)

        with patch('ppio_sandbox.agent_runtime.client.client.AsyncSandbox') as mock_async_sandbox:
            mock_instance = MockAsyncSandbox()
            # Fix: AsyncSandbox.create() is a class method, needs to return AsyncMock
            mock_async_sandbox.create = AsyncMock(return_value=mock_instance)

            sandbox = await client._create_sandbox_instance(
                template_id="test-template",
                timeout_seconds=300,
                config=sandbox_config
            )
        
        assert sandbox is mock_instance
        # Fix: Check create() class method call instead of constructor call
        mock_async_sandbox.create.assert_called_once_with(
            template="test-template",
            timeout=300,
            metadata={"created_by": "agent_runtime_client"},
            envs=sandbox_config.env_vars,
            api_key=test_api_key,
            secure=True,
            auto_pause=False
        )
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_create_sandbox_instance_error(self, test_api_key: str, sandbox_config: SandboxConfig):
        """Test Sandbox instance creation failure"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        with patch('ppio_sandbox.core.AsyncSandbox', side_effect=Exception("Creation failed")):
            with pytest.raises(SandboxCreationError) as exc_info:
                await client._create_sandbox_instance(
                    template_id="test-template",
                    timeout_seconds=300,
                    config=sandbox_config
                )
        
        assert "Failed to create sandbox instance" in str(exc_info.value)


class TestAgentRuntimeClientIntegration:
    """AgentRuntimeClient integration tests"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_client_lifecycle(self, test_api_key: str, sample_template):
        """Test complete client lifecycle"""
        async with AgentRuntimeClient(api_key=test_api_key) as client:
            # 1. Verify initial state
            assert not client._closed
            assert len(client._sessions) == 0
            
            # 2. Mock template exists
            with patch.object(client.template_manager, 'template_exists', return_value=True):
                with patch.object(client, '_create_sandbox_instance') as mock_create:
                    mock_sandbox = MockAsyncSandbox()
                    mock_create.return_value = mock_sandbox
                    
                    # 3. Create session
                    session = await client.create_session(sample_template.template_id)
                    assert len(client._sessions) == 1
                    
                    # 4. List sessions
                    sessions = await client.list_sessions()
                    assert len(sessions) == 1
                    assert sessions[0] is session
                    
                    # 5. Get session
                    found_session = await client.get_session(session.sandbox_id)
                    assert found_session is session
                    
                    # 6. Close session
                    await client.close_session(session.sandbox_id)
                    assert len(client._sessions) == 0
        
        # 7. Client should be closed
        assert client._closed
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_concurrent_session_management(self, test_api_key: str, sample_templates):
        """Test concurrent session management"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        try:
            with patch.object(client.template_manager, 'template_exists', return_value=True):
                with patch.object(client, '_create_sandbox_instance') as mock_create:
                    # Create multiple mock sandboxes
                    mock_sandboxes = [MockAsyncSandbox() for _ in range(3)]
                    mock_create.side_effect = mock_sandboxes
                    
                    # Create sessions concurrently
                    tasks = [
                        client.create_session(template.template_id)
                        for template in sample_templates[:3]
                    ]
                    sessions = await asyncio.gather(*tasks)
                    
                    assert len(sessions) == 3
                    assert len(client._sessions) == 3
                    
                    # Close sessions concurrently
                    close_tasks = [
                        client.close_session(session.sandbox_id)
                        for session in sessions
                    ]
                    await asyncio.gather(*close_tasks)
                    
                    assert len(client._sessions) == 0
        
        finally:
            await client.close()
    
    @pytest.mark.unit
    @pytest.mark.asyncio

    async def test_error_recovery(self, test_api_key: str, sample_template):
        """Test error recovery"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        try:
            # First creation fails
            with patch.object(client.template_manager, 'template_exists', return_value=True):
                with patch.object(client, '_create_sandbox_instance', side_effect=Exception("First failure")):
                    with pytest.raises(SandboxCreationError):
                        await client.create_session(sample_template.template_id)
            
            assert len(client._sessions) == 0
            
            # Second creation succeeds
            with patch.object(client.template_manager, 'template_exists', return_value=True):
                with patch.object(client, '_create_sandbox_instance') as mock_create:
                    mock_sandbox = MockAsyncSandbox()
                    mock_create.return_value = mock_sandbox
                    
                    session = await client.create_session(sample_template.template_id)
                    assert len(client._sessions) == 1
        
        finally:
            await client.close()
    
    @pytest.mark.unit
    def test_client_representation(self, test_api_key: str):
        """Test client string representation"""
        client = AgentRuntimeClient(api_key=test_api_key)
        
        repr_str = repr(client)
        assert "AgentRuntimeClient" in repr_str
        assert "sessions=0" in repr_str
        assert "closed=False" in repr_str
        
        client._closed = True
        repr_str = repr(client)
        assert "closed=True" in repr_str

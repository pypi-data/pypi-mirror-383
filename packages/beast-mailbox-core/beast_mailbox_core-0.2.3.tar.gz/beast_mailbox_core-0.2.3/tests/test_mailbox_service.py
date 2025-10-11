#!/usr/bin/env python3
"""Tests for RedisMailboxService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from beast_mailbox_core import RedisMailboxService, MailboxMessage
from beast_mailbox_core.redis_mailbox import MailboxConfig


@pytest.fixture
def config():
    """Test Redis configuration."""
    return MailboxConfig(
        host="localhost",
        port=6379,
        db=15,
        stream_prefix="test:mailbox",
    )


@pytest.fixture
def agent_id():
    """Test agent ID."""
    return "test-agent"


@pytest.fixture
def service(agent_id, config):
    """Create a mailbox service instance."""
    return RedisMailboxService(agent_id=agent_id, config=config)


class TestMailboxServiceBasics:
    """Test basic RedisMailboxService functionality."""

    def test_service_initialization(self, service, agent_id):
        """Test service initializes with correct agent ID."""
        assert service.agent_id == agent_id
        assert service._client is None
        assert service._running is False
        assert len(service._handlers) == 0

    def test_inbox_stream_property(self, service):
        """Test inbox stream name is formatted correctly."""
        expected = "test:mailbox:test-agent:in"
        assert service.inbox_stream == expected

    def test_consumer_group_naming(self, service):
        """Test consumer group is named correctly."""
        assert service._consumer_group == "test-agent:group"
        assert "test-agent:" in service._consumer_name

    def test_register_handler(self, service):
        """Test registering message handlers."""
        async def handler1(msg):
            pass
        
        async def handler2(msg):
            pass
        
        service.register_handler(handler1)
        assert len(service._handlers) == 1
        
        service.register_handler(handler2)
        assert len(service._handlers) == 2


class TestMailboxServiceMessaging:
    """Test sending messages."""

    @pytest.mark.asyncio
    async def test_send_message_basic(self, service):
        """Test sending a basic message."""
        mock_client = AsyncMock()
        mock_client.xadd = AsyncMock(return_value=b"1234567890-0")
        
        with patch.object(service, '_client', mock_client):
            message_id = await service.send_message(
                recipient="bob",
                payload={"text": "hello"},
            )
            
            assert message_id is not None
            mock_client.xadd.assert_called_once()
            
            # Verify stream name
            call_args = mock_client.xadd.call_args
            assert call_args[0][0] == "test:mailbox:bob:in"

    @pytest.mark.asyncio
    async def test_send_message_with_type(self, service):
        """Test sending message with custom type."""
        mock_client = AsyncMock()
        mock_client.xadd = AsyncMock(return_value=b"1234567890-0")
        
        with patch.object(service, '_client', mock_client):
            message_id = await service.send_message(
                recipient="alice",
                payload={"data": [1, 2, 3]},
                message_type="test_type",
            )
            
            # Verify message was sent
            mock_client.xadd.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


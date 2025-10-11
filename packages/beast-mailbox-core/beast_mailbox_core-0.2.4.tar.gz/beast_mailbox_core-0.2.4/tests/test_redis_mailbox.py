#!/usr/bin/env python3
"""Tests for RedisMailboxService core functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from beast_mailbox_core import RedisMailboxService, MailboxMessage
from beast_mailbox_core.redis_mailbox import MailboxConfig


@pytest.fixture
def config():
    """Test configuration."""
    return MailboxConfig(host="localhost", port=6379, db=15)


@pytest.fixture
def service(config):
    """Create service instance."""
    return RedisMailboxService("test-agent", config)


class TestServiceLifecycle:
    """Test service lifecycle without actual Redis connections."""

    @pytest.mark.asyncio
    async def test_connect_creates_client(self, service):
        """Test connect creates Redis client."""
        with patch('beast_mailbox_core.redis_mailbox.redis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            await service.connect()
            
            assert service._client == mock_client
            mock_redis.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_success(self, service):
        """Test successful service start."""
        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock()
        
        with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
            result = await service.start()
            
            assert result is True
            assert service._running is True
            assert service._processing_task is not None
            mock_client.xgroup_create.assert_called_once()
            
            # Clean up - cancel the task
            await service.stop()

    @pytest.mark.asyncio
    async def test_start_with_busygroup_succeeds(self, service):
        """Test start succeeds even with BUSYGROUP error."""
        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock(
            side_effect=Exception("BUSYGROUP Consumer Group name already exists")
        )
        
        with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
            result = await service.start()
            
            assert result is True
            assert service._running is True
            
            await service.stop()

    @pytest.mark.asyncio
    async def test_start_raises_non_busygroup_errors(self, service):
        """Test start raises other exceptions."""
        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock(
            side_effect=Exception("Permission denied")
        )
        
        with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
            with pytest.raises(Exception, match="Permission denied"):
                await service.start()

    @pytest.mark.asyncio
    async def test_stop_without_start(self, service):
        """Test stop works when service never started."""
        await service.stop()
        
        assert service._running is False
        assert service._client is None

    @pytest.mark.asyncio
    async def test_stop_closes_client(self, service):
        """Test stop closes Redis client."""
        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        service._client = mock_client
        
        await service.stop()
        
        mock_client.close.assert_called_once()
        assert service._client is None

    @pytest.mark.asyncio
    async def test_stop_cancels_processing_task(self, service):
        """Test stop cancels and waits for processing task."""
        service._running = True
        
        # Create a real async task that we can cancel
        async def dummy_task():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                pass
        
        service._processing_task = asyncio.create_task(dummy_task())
        
        await service.stop()
        
        assert service._processing_task is None
        assert service._running is False

    @pytest.mark.asyncio
    async def test_stop_handles_task_with_exception(self, service):
        """Test stop handles tasks that raise non-CancelledError exceptions."""
        service._running = True
        
        # Create a task that will raise a different exception
        async def failing_task():
            await asyncio.sleep(0.01)
            raise RuntimeError("Task failed during shutdown")
        
        service._processing_task = asyncio.create_task(failing_task())
        
        # Give task a moment to start
        await asyncio.sleep(0.02)
        
        # stop() should handle the exception gracefully
        await service.stop()
        
        assert service._processing_task is None
        assert service._running is False


class TestMessageDispatching:
    """Test message dispatching to handlers."""

    @pytest.mark.asyncio
    async def test_dispatch_no_handlers(self, service):
        """Test dispatch with no handlers logs but doesn't crash."""
        message = MailboxMessage(
            message_id="test-id",
            sender="alice",
            recipient="test-agent",
            payload={"text": "hello"}
        )
        
        # Should not raise
        await service._dispatch(message)

    @pytest.mark.asyncio
    async def test_dispatch_single_handler(self, service):
        """Test dispatch calls handler."""
        received_messages = []
        
        async def handler(msg):
            received_messages.append(msg)
        
        service.register_handler(handler)
        
        message = MailboxMessage(
            message_id="test-id",
            sender="alice",
            recipient="test-agent",
            payload={"text": "hello"}
        )
        
        await service._dispatch(message)
        
        assert len(received_messages) == 1
        assert received_messages[0].sender == "alice"

    @pytest.mark.asyncio
    async def test_dispatch_multiple_handlers(self, service):
        """Test dispatch calls all handlers."""
        call_count = [0]
        
        async def handler1(msg):
            call_count[0] += 1
        
        async def handler2(msg):
            call_count[0] += 1
        
        service.register_handler(handler1)
        service.register_handler(handler2)
        
        message = MailboxMessage(
            message_id="test-id",
            sender="alice",
            recipient="test-agent",
            payload={"text": "hello"}
        )
        
        await service._dispatch(message)
        
        assert call_count[0] == 2

    @pytest.mark.asyncio
    async def test_dispatch_handler_error_doesnt_crash(self, service):
        """Test that handler errors are caught and logged."""
        handler2_called = False
        
        async def failing_handler(msg):
            raise ValueError("Handler failed!")
        
        async def good_handler(msg):
            nonlocal handler2_called
            handler2_called = True
        
        service.register_handler(failing_handler)
        service.register_handler(good_handler)
        
        message = MailboxMessage(
            message_id="test-id",
            sender="alice",
            recipient="test-agent",
            payload={"text": "hello"}
        )
        
        # Should not raise, just log error
        await service._dispatch(message)
        
        # Second handler should still run
        assert handler2_called


class TestSendMessage:
    """Test sending messages."""

    @pytest.mark.asyncio
    async def test_send_message_connects_first(self, service):
        """Test send_message calls connect if not connected."""
        mock_client = AsyncMock()
        mock_client.xadd = AsyncMock(return_value=b"1234567890-0")
        
        with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
            message_id = await service.send_message(
                recipient="bob",
                payload={"text": "hello"}
            )
            
            assert service._client is not None
            assert message_id is not None

    @pytest.mark.asyncio
    async def test_send_message_formats_stream_correctly(self, service):
        """Test send_message uses correct stream name."""
        mock_client = AsyncMock()
        mock_client.xadd = AsyncMock(return_value=b"1234567890-0")
        service._client = mock_client
        
        await service.send_message(
            recipient="bob",
            payload={"text": "hello"}
        )
        
        # Verify stream name (uses default prefix "beast:mailbox")
        call_args = mock_client.xadd.call_args
        assert call_args[0][0] == "beast:mailbox:bob:in"

    @pytest.mark.asyncio
    async def test_send_message_with_custom_id(self, service):
        """Test send_message with custom message ID."""
        mock_client = AsyncMock()
        mock_client.xadd = AsyncMock(return_value=b"1234567890-0")
        service._client = mock_client
        
        message_id = await service.send_message(
            recipient="bob",
            payload={"text": "hello"},
            message_id="custom-id-123"
        )
        
        # Returns the custom ID
        assert message_id == "custom-id-123"

    @pytest.mark.asyncio
    async def test_send_message_respects_maxlen(self, service):
        """Test send_message uses configured max_stream_length."""
        mock_client = AsyncMock()
        mock_client.xadd = AsyncMock(return_value=b"1234567890-0")
        service._client = mock_client
        
        await service.send_message(
            recipient="bob",
            payload={"text": "hello"}
        )
        
        # Verify maxlen parameter
        call_args = mock_client.xadd.call_args
        assert call_args[1]['maxlen'] == service.config.max_stream_length
        assert call_args[1]['approximate'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


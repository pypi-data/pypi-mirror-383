#!/usr/bin/env python3
"""Tests for CLI functions and _fetch_latest_messages."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from beast_mailbox_core import RedisMailboxService
from beast_mailbox_core.redis_mailbox import MailboxConfig
from beast_mailbox_core.cli import _fetch_latest_messages


@pytest.fixture
async def mock_service():
    """Create a service with fully mocked client that won't reset."""
    config = MailboxConfig(host="localhost", db=15)
    service = RedisMailboxService("test-agent", config)
    
    # Create mock client
    mock_client = AsyncMock()
    mock_client.xrevrange = AsyncMock(return_value=[])
    mock_client.xgroup_create = AsyncMock()
    mock_client.xack = AsyncMock(return_value=0)
    mock_client.xdel = AsyncMock(return_value=0)
    mock_client.close = AsyncMock()
    
    # Actually call connect to set client
    with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
        await service.connect()
    
    # Override stop to not clear client
    original_stop = service.stop
    async def mock_stop():
        service._running = False
        # Don't clear _client
    service.stop = mock_stop
    
    yield service, mock_client
    
    # Cleanup
    await original_stop()


@pytest.fixture
def sample_redis_messages():
    """Sample Redis stream messages."""
    return [
        (
            b"1234567890-0",
            {
                b"message_id": b"msg-001",
                b"sender": b"alice",
                b"recipient": b"test-agent",
                b"payload": b'{"text": "Hello"}',
                b"message_type": b"greeting",
                b"timestamp": b"123.456",
            },
        ),
        (
            b"1234567891-0",
            {
                b"message_id": b"msg-002",
                b"sender": b"bob",
                b"recipient": b"test-agent",
                b"payload": b'{"count": 42}',
                b"message_type": b"data",
                b"timestamp": b"124.456",
            },
        ),
    ]


class TestFetchLatestMessages:
    """Test the _fetch_latest_messages CLI function."""

    @pytest.mark.asyncio
    async def test_fetch_no_messages(self, mock_service):
        """Test fetching when stream is empty."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=[])
        
        await _fetch_latest_messages(service, count=10, ack=False, trim=False)
        
        client.xrevrange.assert_called_once()
        assert client.xrevrange.call_args[0][0] == service.inbox_stream
        assert client.xrevrange.call_args[1]['count'] == 10

    @pytest.mark.asyncio
    async def test_fetch_displays_messages(self, mock_service, sample_redis_messages):
        """Test fetching and displaying messages."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=sample_redis_messages)
        
        await _fetch_latest_messages(service, count=2, ack=False, trim=False)
        
        client.xrevrange.assert_called_once()
        # Should not ack or delete
        client.xack.assert_not_called()
        client.xdel.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_with_ack(self, mock_service, sample_redis_messages):
        """Test fetching with acknowledgment."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=sample_redis_messages)
        client.xack = AsyncMock(return_value=2)
        
        await _fetch_latest_messages(service, count=2, ack=True, trim=False)
        
        # Should create consumer group
        client.xgroup_create.assert_called_once()
        # Should ack messages
        client.xack.assert_called_once()
        # Should NOT delete
        client.xdel.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_with_ack_and_trim(self, mock_service, sample_redis_messages):
        """Test fetching with ack and trim."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=sample_redis_messages)
        client.xack = AsyncMock(return_value=2)
        client.xdel = AsyncMock(return_value=2)
        
        await _fetch_latest_messages(service, count=2, ack=True, trim=True)
        
        # Should ack first
        client.xack.assert_called_once()
        # Then delete
        client.xdel.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_ack_handles_busygroup(self, mock_service, sample_redis_messages):
        """Test ack handles BUSYGROUP error gracefully."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=sample_redis_messages)
        client.xgroup_create = AsyncMock(
            side_effect=Exception("BUSYGROUP Consumer Group name already exists")
        )
        client.xack = AsyncMock(return_value=2)
        
        await _fetch_latest_messages(service, count=2, ack=True, trim=False)
        
        # Should still ack despite BUSYGROUP
        client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_ack_handles_non_busygroup_error(self, mock_service, sample_redis_messages):
        """Test ack logs warning for non-BUSYGROUP errors."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=sample_redis_messages)
        client.xgroup_create = AsyncMock(
            side_effect=Exception("Permission denied")
        )
        client.xack = AsyncMock(return_value=2)
        
        # Should handle gracefully and still try to ack
        await _fetch_latest_messages(service, count=2, ack=True, trim=False)
        
        client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_ack_failure_raises_systemexit(self, mock_service, sample_redis_messages):
        """Test ack failure raises SystemExit."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=sample_redis_messages)
        client.xack = AsyncMock(side_effect=Exception("Redis connection lost"))
        
        with pytest.raises(SystemExit, match="Acknowledgement failed"):
            await _fetch_latest_messages(service, count=2, ack=True, trim=False)

    @pytest.mark.asyncio
    async def test_fetch_trim_failure_raises_systemexit(self, mock_service, sample_redis_messages):
        """Test trim failure raises SystemExit."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=sample_redis_messages)
        client.xack = AsyncMock(return_value=2)
        client.xdel = AsyncMock(side_effect=Exception("Delete failed"))
        
        with pytest.raises(SystemExit, match="Deletion failed"):
            await _fetch_latest_messages(service, count=2, ack=True, trim=True)

    @pytest.mark.asyncio
    async def test_fetch_only_acks_if_messages_exist(self, mock_service):
        """Test ack flag is ignored when no messages."""
        service, client = mock_service
        client.xrevrange = AsyncMock(return_value=[])
        
        # ack=True but no messages, so xack shouldn't be called
        await _fetch_latest_messages(service, count=10, ack=True, trim=False)
        
        client.xrevrange.assert_called_once()
        client.xack.assert_not_called()
        client.xdel.assert_not_called()


class TestCLIArgumentParsing:
    """Test CLI argument parsing without running async code."""

    def test_run_service_creates_config(self):
        """Test run_service creates correct MailboxConfig."""
        from beast_mailbox_core.cli import run_service
        
        with patch('beast_mailbox_core.cli.asyncio.run') as mock_run:
            run_service([
                'my-agent',
                '--redis-host', '192.168.1.100',
                '--redis-port', '6380',
                '--redis-password', 'secret',
                '--redis-db', '2',
                '--stream-prefix', 'custom:prefix',
                '--maxlen', '500',
                '--poll-interval', '1.5',
            ])
            
            # Verify asyncio.run was called with coroutine
            mock_run.assert_called_once()

    def test_send_message_parses_json(self):
        """Test send_message parses JSON payload."""
        from beast_mailbox_core.cli import send_message
        
        with patch('beast_mailbox_core.cli.asyncio.run') as mock_run:
            send_message([
                'alice', 'bob',
                '--json', '{"key": "value", "count": 42}',
            ])
            
            mock_run.assert_called_once()

    def test_send_message_uses_text_message(self):
        """Test send_message with --message flag."""
        from beast_mailbox_core.cli import send_message
        
        with patch('beast_mailbox_core.cli.asyncio.run') as mock_run:
            send_message([
                'alice', 'bob',
                '--message', 'hello world',
            ])
            
            mock_run.assert_called_once()


class TestCLIAsyncFunctions:
    """Test async CLI functions with proper mocking."""

    @pytest.mark.asyncio
    async def test_send_message_async_with_text(self):
        """Test send_message_async sends text message."""
        from beast_mailbox_core.cli import send_message_async
        import argparse
        
        args = argparse.Namespace(
            sender='alice',
            recipient='bob',
            message='hello',
            json=None,
            message_type='direct_message',
            redis_host='localhost',
            redis_port=6379,
            redis_password=None,
            redis_db=0,
            stream_prefix='beast:mailbox',
        )
        
        with patch('beast_mailbox_core.cli.RedisMailboxService') as mock_svc_class:
            mock_service = AsyncMock()
            mock_service.send_message = AsyncMock()
            mock_service.stop = AsyncMock()
            mock_svc_class.return_value = mock_service
            
            await send_message_async(args)
            
            # Verify message sent
            mock_service.send_message.assert_called_once()
            call_kwargs = mock_service.send_message.call_args[1]
            assert call_kwargs['recipient'] == 'bob'
            assert call_kwargs['payload'] == {'message': 'hello'}
            
            # Verify cleanup
            mock_service.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_async_with_json(self):
        """Test send_message_async sends JSON payload."""
        from beast_mailbox_core.cli import send_message_async
        import argparse
        
        args = argparse.Namespace(
            sender='alice',
            recipient='bob',
            message=None,
            json='{"key": "value", "count": 42}',
            message_type='data',
            redis_host='localhost',
            redis_port=6379,
            redis_password=None,
            redis_db=0,
            stream_prefix='beast:mailbox',
        )
        
        with patch('beast_mailbox_core.cli.RedisMailboxService') as mock_svc_class:
            mock_service = AsyncMock()
            mock_service.send_message = AsyncMock()
            mock_service.stop = AsyncMock()
            mock_svc_class.return_value = mock_service
            
            await send_message_async(args)
            
            # Verify JSON was parsed
            call_kwargs = mock_service.send_message.call_args[1]
            assert call_kwargs['payload'] == {"key": "value", "count": 42}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


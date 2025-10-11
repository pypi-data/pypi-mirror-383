#!/usr/bin/env python3
"""Edge case and integration tests for mailbox service."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from beast_mailbox_core import RedisMailboxService, MailboxMessage
from beast_mailbox_core.redis_mailbox import MailboxConfig


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_send_message_with_empty_payload(self):
        """Test sending a message with empty dict payload."""
        config = MailboxConfig(host="localhost", db=15)
        service = RedisMailboxService("test-agent", config)
        
        mock_client = AsyncMock()
        mock_client.xadd = AsyncMock(return_value=b"123-0")
        
        with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
            msg_id = await service.send_message("recipient", {})
            
            assert msg_id is not None
            mock_client.xadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_with_nested_payload(self):
        """Test sending a message with deeply nested payload."""
        config = MailboxConfig(host="localhost", db=15)
        service = RedisMailboxService("test-agent", config)
        
        mock_client = AsyncMock()
        mock_client.xadd = AsyncMock(return_value=b"123-0")
        
        complex_payload = {
            "level1": {
                "level2": {
                    "level3": ["a", "b", "c"],
                    "number": 42
                },
                "list": [1, 2, {"nested": True}]
            }
        }
        
        with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
            msg_id = await service.send_message("recipient", complex_payload)
            
            assert msg_id is not None

    @pytest.mark.asyncio
    async def test_service_lifecycle_complete_flow(self):
        """Test complete start/stop lifecycle with mocked loop."""
        config = MailboxConfig(host="localhost", db=15)
        service = RedisMailboxService("test-agent", config)
        
        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock()
        
        # Track if loop was created
        loop_created = False
        original_create_task = asyncio.create_task
        
        def mock_create_task(coro):
            nonlocal loop_created
            loop_created = True
            # Cancel immediately to prevent blocking
            task = original_create_task(coro)
            task.cancel()
            return task
        
        with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
            with patch('asyncio.create_task', side_effect=mock_create_task):
                await service.start()
                assert loop_created is True
                await service.stop()
                
                assert service._running is False

    @pytest.mark.asyncio
    async def test_multiple_handlers_execution_order(self):
        """Test that multiple handlers execute in registration order."""
        config = MailboxConfig(host="localhost", db=15)
        service = RedisMailboxService("test-agent", config)
        
        execution_order = []
        
        async def handler1(msg):
            execution_order.append(1)
        
        async def handler2(msg):
            execution_order.append(2)
        
        async def handler3(msg):
            execution_order.append(3)
        
        service.register_handler(handler1)
        service.register_handler(handler2)
        service.register_handler(handler3)
        
        message = MailboxMessage(
            message_id="test",
            sender="alice",
            recipient="bob",
            payload={"test": True}
        )
        
        await service._dispatch(message)
        
        assert execution_order == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_config_with_all_custom_values(self):
        """Test MailboxConfig with every parameter customized."""
        config = MailboxConfig(
            host="redis.example.com",
            port=6380,
            password="super-secret",
            db=7,
            stream_prefix="custom:prefix",
            max_stream_length=5000,
            poll_interval=1.5
        )
        
        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.password == "super-secret"
        assert config.db == 7
        assert config.stream_prefix == "custom:prefix"
        assert config.max_stream_length == 5000
        assert config.poll_interval == 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


#!/usr/bin/env python3
"""Tests for CLI helper functions (_acknowledge_messages, _trim_messages)."""

import pytest
from unittest.mock import AsyncMock

from beast_mailbox_core.cli import _acknowledge_messages, _trim_messages


class TestAcknowledgeMessages:
    """Test the _acknowledge_messages helper function."""

    @pytest.mark.asyncio
    async def test_acknowledge_creates_group_and_acks(self):
        """Test successful acknowledgment with group creation."""
        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock()
        mock_client.xack = AsyncMock(return_value=3)
        
        await _acknowledge_messages(
            mock_client,
            "test:stream",
            "test:group",
            [b"msg1", b"msg2", b"msg3"]
        )
        
        mock_client.xgroup_create.assert_called_once()
        mock_client.xack.assert_called_once_with("test:stream", "test:group", b"msg1", b"msg2", b"msg3")

    @pytest.mark.asyncio
    async def test_acknowledge_with_non_busygroup_error(self):
        """Test ack logs warning for non-BUSYGROUP errors during group creation."""
        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock(side_effect=Exception("Permission denied"))
        mock_client.xack = AsyncMock(return_value=1)
        
        # Should log warning but still attempt to ack
        await _acknowledge_messages(
            mock_client,
            "test:stream",
            "test:group",
            [b"msg1"]
        )
        
        # Should still try to ack despite group creation failure
        mock_client.xack.assert_called_once()


class TestTrimMessages:
    """Test the _trim_messages helper function."""

    @pytest.mark.asyncio
    async def test_trim_deletes_messages(self):
        """Test successful message deletion."""
        mock_client = AsyncMock()
        mock_client.xdel = AsyncMock(return_value=2)
        
        await _trim_messages(
            mock_client,
            "test:stream",
            [b"msg1", b"msg2"]
        )
        
        mock_client.xdel.assert_called_once_with("test:stream", b"msg1", b"msg2")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


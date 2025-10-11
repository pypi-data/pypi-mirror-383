#!/usr/bin/env python3
"""Tests for MailboxMessage class."""

import json
import pytest

from beast_mailbox_core import MailboxMessage


class TestMailboxMessageDecoding:
    """Test MailboxMessage payload decoding with various field types."""

    def test_from_redis_fields_with_bytes(self):
        """Test decoding Redis fields when all values are bytes."""
        fields = {
            b"message_id": b"msg-001",
            b"sender": b"alice",
            b"recipient": b"bob",
            b"payload": b'{"text": "Hello"}',
            b"message_type": b"direct_message",
            b"timestamp": b"1234567890.0",
        }
        
        message = MailboxMessage.from_redis_fields(fields)
        
        assert message.message_id == "msg-001"
        assert message.sender == "alice"
        assert message.recipient == "bob"
        assert message.payload == {"text": "Hello"}
        assert message.message_type == "direct_message"
        assert message.timestamp == 1234567890.0

    def test_from_redis_fields_complex_payload(self):
        """Test decoding Redis fields with complex JSON payload."""
        fields = {
            b"message_id": b"msg-002",
            b"sender": b"charlie",
            b"recipient": b"dave",
            b"payload": b'{"count": 42, "tags": ["test", "prod"], "meta": {"version": 2}}',
            b"message_type": b"notification",
            b"timestamp": b"9876543210.5",
        }
        
        message = MailboxMessage.from_redis_fields(fields)
        
        assert message.message_id == "msg-002"
        assert message.sender == "charlie"
        assert message.recipient == "dave"
        assert message.payload == {"count": 42, "tags": ["test", "prod"], "meta": {"version": 2}}
        assert message.message_type == "notification"
        assert message.timestamp == 9876543210.5

    def test_from_redis_fields_empty_payload(self):
        """Test decoding Redis fields with empty payload."""
        fields = {
            b"message_id": b"msg-003",
            b"sender": b"eve",
            b"recipient": b"frank",
            b"payload": b'{}',
            b"message_type": b"status_update",
            b"timestamp": b"1111111111.0",
        }
        
        message = MailboxMessage.from_redis_fields(fields)
        
        assert message.message_id == "msg-003"
        assert message.sender == "eve"
        assert message.recipient == "frank"
        assert message.payload == {}
        assert message.message_type == "status_update"
        assert message.timestamp == 1111111111.0

    def test_to_redis_fields(self):
        """Test encoding message to Redis fields."""
        message = MailboxMessage(
            message_id="test-id",
            sender="alice",
            recipient="bob",
            payload={"key": "value"},
            message_type="test_message",
            timestamp=123.456
        )
        
        fields = message.to_redis_fields()
        
        assert fields["message_id"] == "test-id"
        assert fields["sender"] == "alice"
        assert fields["recipient"] == "bob"
        assert json.loads(fields["payload"]) == {"key": "value"}
        assert fields["message_type"] == "test_message"
        assert fields["timestamp"] == "123.456"

    def test_missing_fields_use_defaults(self):
        """Test that missing fields use appropriate defaults."""
        fields = {
            b"payload": b'{"text": "test"}',
        }
        
        message = MailboxMessage.from_redis_fields(fields)
        
        assert message.sender == "unknown"
        assert message.recipient == "unknown"
        assert message.message_type == "direct_message"
        assert message.payload == {"text": "test"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


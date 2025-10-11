#!/usr/bin/env python3
"""Tests for MailboxConfig class."""

import pytest

from beast_mailbox_core.redis_mailbox import MailboxConfig


class TestMailboxConfig:
    """Test MailboxConfig defaults and initialization."""

    def test_default_config(self):
        """Test that defaults are set correctly."""
        config = MailboxConfig()
        
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None
        assert config.stream_prefix == "beast:mailbox"
        assert config.max_stream_length == 1000
        assert config.poll_interval == 2.0

    def test_custom_config(self):
        """Test creating config with custom values."""
        config = MailboxConfig(
            host="redis.example.com",
            port=6380,
            db=5,
            password="secret",
            stream_prefix="custom:prefix",
            max_stream_length=5000,
            poll_interval=1.5,
        )
        
        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.db == 5
        assert config.password == "secret"
        assert config.stream_prefix == "custom:prefix"
        assert config.max_stream_length == 5000
        assert config.poll_interval == 1.5

    def test_partial_config(self):
        """Test creating config with some custom values."""
        config = MailboxConfig(
            host="192.168.1.100",
            password="mypass"
        )
        
        assert config.host == "192.168.1.100"
        assert config.password == "mypass"
        # Other values should still be defaults
        assert config.port == 6379
        assert config.stream_prefix == "beast:mailbox"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


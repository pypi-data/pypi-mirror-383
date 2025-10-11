"""Command line entry points for the mailbox service.

This module provides CLI tools for interacting with the Beast Mailbox Core:
    - beast-mailbox-service: Start a mailbox listener/inspector
    - beast-mailbox-send: Send messages to other agents

The CLI supports both one-shot operations (inspect/send) and long-running
service mode (continuous message consumption with handlers).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from typing import Any, Dict

from .redis_mailbox import MailboxConfig, MailboxMessage, RedisMailboxService


def configure_logging(verbose: bool) -> None:
    """Configure logging for CLI operations.
    
    Args:
        verbose: If True, set DEBUG level; otherwise INFO level
        
    The format includes timestamp, level, logger name, and message for
    comprehensive log output during CLI operations.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


async def _acknowledge_messages(
    client: Any,
    stream: str,
    consumer_group: str,
    message_ids: list,
) -> None:
    """Acknowledge messages in a consumer group after processing.
    
    Args:
        client: Redis client instance
        stream: Stream name containing the messages
        consumer_group: Consumer group name for acknowledgment
        message_ids: List of message IDs to acknowledge
        
    Raises:
        SystemExit: If acknowledgment fails (with error details)
        
    Note:
        This function creates the consumer group if it doesn't exist,
        handling BUSYGROUP errors gracefully. Other group creation
        errors are logged as warnings but don't prevent acknowledgment.
    """
    try:
        # Ensure consumer group exists
        try:
            await client.xgroup_create(
                name=stream,
                groupname=consumer_group,
                id="0",
                mkstream=True,
            )
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                logging.warning("Could not create consumer group: %s", exc)

        # Acknowledge messages
        ack_count = await client.xack(stream, consumer_group, *message_ids)
        logging.info("✓ Acknowledged %d message(s) in group %s", ack_count, consumer_group)
    except Exception as exc:
        logging.error("Failed to acknowledge messages: %s", exc)
        raise SystemExit(f"Acknowledgement failed: {exc}")


async def _trim_messages(
    client: Any,
    stream: str,
    message_ids: list,
) -> None:
    """Delete messages from a stream using XDEL.
    
    Args:
        client: Redis client instance
        stream: Stream name containing the messages
        message_ids: List of message IDs to delete
        
    Raises:
        SystemExit: If deletion fails (with error details)
        
    Note:
        This is useful for cleaning up messages after inspection or
        processing. Unlike stream trimming by length, this allows
        selective deletion of specific messages.
    """
    try:
        delete_count = await client.xdel(stream, *message_ids)
        logging.info("🗑️  Deleted %d message(s) from stream", delete_count)
    except Exception as exc:
        logging.error("Failed to delete messages: %s", exc)
        raise SystemExit(f"Deletion failed: {exc}")


async def _fetch_latest_messages(
    service: RedisMailboxService,
    count: int,
    ack: bool = False,
    trim: bool = False,
) -> None:
    """Retrieve and display the latest messages from the inbox without starting a consumer loop.
    
    This is a one-shot inspection tool for checking mailbox contents. It reads
    messages in reverse chronological order (newest first) without blocking.
    
    Args:
        service: The mailbox service instance to use for retrieval
        count: Maximum number of messages to retrieve (default: 10)
        ack: If True, acknowledge messages in the consumer group after display
        trim: If True, delete messages from the stream after acknowledging
        
    Raises:
        SystemExit: If Redis client is unavailable or operations fail
        
    Example:
        >>> service = RedisMailboxService("my-agent", config)
        >>> await _fetch_latest_messages(service, count=5, ack=True)
        
    Note:
        The --ack flag marks messages as processed in the consumer group.
        The --trim flag permanently deletes messages (use with caution).
        Both flags can be combined for "read and delete" behavior.
    """
    await service.connect()
    client = service._client
    if client is None:
        raise SystemExit("Redis client unavailable after connection")

    try:
        stream = service.inbox_stream
        entries = await client.xrevrange(stream, count=count)

        if not entries:
            logging.info("No messages found in %s", stream)
            return

        message_ids = []
        for message_id, fields in entries:
            mailbox_message = MailboxMessage.from_redis_fields(fields)
            logging.info(
                "📬 %s <- %s (%s) [%s]: %s",
                mailbox_message.recipient,
                mailbox_message.sender,
                mailbox_message.message_type,
                message_id,
                mailbox_message.payload,
            )
            message_ids.append(message_id)

        # Handle operations if requested
        if ack and message_ids:
            consumer_group = f"{service.agent_id}:group"
            await _acknowledge_messages(client, stream, consumer_group, message_ids)

        if trim and message_ids:
            await _trim_messages(client, stream, message_ids)

    finally:
        await service.stop()


async def run_service_async(args: argparse.Namespace) -> None:
    """Async implementation of the mailbox service command.
    
    This function provides two modes of operation:
    1. One-shot mode (--latest flag): Inspect recent messages and exit
    2. Service mode: Run continuously, consuming and handling messages
    
    Args:
        args: Parsed command-line arguments containing:
            - agent_id: Agent identifier for this instance
            - redis_host, redis_port, redis_password, redis_db: Redis connection
            - stream_prefix: Prefix for stream names
            - maxlen: Maximum stream length (MAXLEN parameter)
            - poll_interval: Polling interval for message consumption
            - latest: If True, run in one-shot inspection mode
            - count: Number of messages to fetch in one-shot mode
            - ack: Acknowledge messages in one-shot mode
            - trim: Delete messages in one-shot mode
            - echo: Register an echo handler that logs all received messages
            
    Raises:
        SystemExit: If service fails to start or Redis connection fails
        
    Note:
        In service mode, the function runs until interrupted (Ctrl+C) or
        cancelled. The service gracefully shuts down on interruption.
    """
    config = MailboxConfig(
        host=args.redis_host,
        port=args.redis_port,
        password=args.redis_password,
        db=args.redis_db,
        stream_prefix=args.stream_prefix,
        max_stream_length=args.maxlen,
        poll_interval=args.poll_interval,
    )

    service = RedisMailboxService(agent_id=args.agent_id, config=config)

    # Handle one-shot latest message retrieval
    if args.latest:
        await _fetch_latest_messages(service, args.count, args.ack, args.trim)
        return

    # Streaming mode - echo handler
    async def echo_handler(message: MailboxMessage) -> None:
        """Echo received messages to console."""
        logging.info(
            "📬 %s <- %s (%s): %s",
            message.recipient,
            message.sender,
            message.message_type,
            message.payload,
        )
        # Yield to event loop (proper async pattern for I/O-less async functions)
        await asyncio.sleep(0)

    if args.echo:
        service.register_handler(echo_handler)

    if not await service.start():
        raise SystemExit("Failed to start mailbox service")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Stopping mailbox service...")
    finally:
        await service.stop()
        logging.info("Mailbox service stopped")


def run_service(argv: list[str] | None = None) -> None:
    """CLI entry point for beast-mailbox-service command.
    
    Starts the Beast Mailbox service for an agent. The service can run in
    two modes:
    
    1. **Inspector Mode** (--latest flag):
       Fetch and display recent messages, optionally acknowledge/trim them, then exit.
       
    2. **Service Mode** (default):
       Run continuously, consuming messages and dispatching to handlers.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv if None)
        
    Command-line Arguments:
        agent_id (required): Unique identifier for this agent
        --redis-host: Redis server hostname (default: localhost)
        --redis-port: Redis server port (default: 6379)
        --redis-password: Optional Redis password
        --redis-db: Redis database number (default: 0)
        --stream-prefix: Prefix for stream names (default: beast:mailbox)
        --maxlen: Maximum stream length (default: 1000)
        --poll-interval: Polling interval in seconds (default: 2.0)
        --echo: Register an echo handler that prints received messages
        --latest: Run in one-shot inspection mode
        --count: Number of messages to fetch (default: 10, with --latest)
        --ack: Acknowledge messages after display (with --latest)
        --trim: Delete messages after acknowledgment (with --latest)
        --verbose: Enable DEBUG logging
        
    Examples:
        # Start a service that echoes messages:
        $ beast-mailbox-service my-agent --echo --verbose
        
        # Inspect last 5 messages without acknowledging:
        $ beast-mailbox-service my-agent --latest --count 5
        
        # Read and delete last 10 messages:
        $ beast-mailbox-service my-agent --latest --ack --trim
        
    Raises:
        SystemExit: On configuration errors or service failures
    """
    parser = argparse.ArgumentParser(description="Run Beast mailbox service")
    parser.add_argument("agent_id", help="Agent identifier for this instance")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=6379)
    parser.add_argument("--redis-password", default=None)
    parser.add_argument("--redis-db", type=int, default=0)
    parser.add_argument("--stream-prefix", default="beast:mailbox")
    parser.add_argument("--maxlen", type=int, default=1000, help="Max stream length")
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--echo", action="store_true", help="Print received messages to stdout")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Print the latest message(s) and exit instead of streaming",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of latest messages to display when using --latest",
    )
    parser.add_argument(
        "--ack",
        action="store_true",
        help="Acknowledge messages after displaying them (requires --latest)",
    )
    parser.add_argument(
        "--trim",
        action="store_true",
        help="Delete messages after acknowledging them (requires --latest and --ack)",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    asyncio.run(run_service_async(args))


async def send_message_async(args: argparse.Namespace) -> None:
    """Async implementation of the send message command.
    
    Sends a single message to a recipient agent's inbox and exits.
    
    Args:
        args: Parsed command-line arguments containing:
            - sender: Sending agent ID
            - recipient: Receiving agent ID
            - message: Plain text message (optional)
            - json: JSON string payload (optional, takes precedence over message)
            - message_type: Message classification
            - redis_host, redis_port, redis_password, redis_db: Redis connection
            - stream_prefix: Prefix for stream names
            
    Raises:
        SystemExit: If Redis connection fails or message cannot be sent
        json.JSONDecodeError: If --json contains invalid JSON
        
    Note:
        Either --message or --json must be provided (not both).
        The service connects, sends the message, and disconnects cleanly.
    """
    config = MailboxConfig(
        host=args.redis_host,
        port=args.redis_port,
        password=args.redis_password,
        db=args.redis_db,
        stream_prefix=args.stream_prefix,
    )
    service = RedisMailboxService(agent_id=args.sender, config=config)
    payload: Dict[str, Any]
    if args.json:
        payload = json.loads(args.json)
    else:
        payload = {"message": args.message}
    await service.send_message(recipient=args.recipient, payload=payload, message_type=args.message_type)
    await service.stop()
    logging.info("Sent message from %s to %s", args.sender, args.recipient)


def send_message(argv: list[str] | None = None) -> None:
    """CLI entry point for beast-mailbox-send command.
    
    Send a message from one agent to another agent's inbox. This is a
    one-shot operation that connects, sends, and disconnects cleanly.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv if None)
        
    Command-line Arguments:
        sender (required): Sending agent ID
        recipient (required): Receiving agent ID
        --message: Plain text message (mutually exclusive with --json)
        --json: JSON string payload (mutually exclusive with --message)
        --message-type: Message classification (default: direct_message)
        --redis-host: Redis server hostname (default: localhost)
        --redis-port: Redis server port (default: 6379)
        --redis-password: Optional Redis password
        --redis-db: Redis database number (default: 0)
        --stream-prefix: Prefix for stream names (default: beast:mailbox)
        --verbose: Enable DEBUG logging
        
    Examples:
        # Send a text message:
        $ beast-mailbox-send alice bob --message "Hello!"
        
        # Send structured JSON data:
        $ beast-mailbox-send alice bob --json '{"action": "deploy", "version": "1.2.3"}'
        
        # Send with custom message type:
        $ beast-mailbox-send alice bob --json '{"status": "ok"}' --message-type health_check
        
    Raises:
        SystemExit: On configuration errors, connection failures, or invalid JSON
        
    Note:
        You must provide either --message OR --json (not both).
        The --json payload must be valid JSON.
    """
    parser = argparse.ArgumentParser(description="Send message via Beast mailbox")
    parser.add_argument("sender", help="Sender agent id")
    parser.add_argument("recipient", help="Recipient agent id")
    parser.add_argument("--message", default="hello")
    parser.add_argument("--json")
    parser.add_argument("--message-type", default="direct_message")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=6379)
    parser.add_argument("--redis-password", default=None)
    parser.add_argument("--redis-db", type=int, default=0)
    parser.add_argument("--stream-prefix", default="beast:mailbox")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    asyncio.run(send_message_async(args))


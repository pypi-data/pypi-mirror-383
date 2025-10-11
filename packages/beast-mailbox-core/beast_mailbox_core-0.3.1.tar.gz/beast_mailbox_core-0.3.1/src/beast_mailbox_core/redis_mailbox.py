"""Lightweight Redis-backed mailbox service for inter-agent messaging."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional
from uuid import uuid4

import redis.asyncio as redis


@dataclass
class MailboxConfig:
    """Configuration for connecting to Redis streams."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    stream_prefix: str = "beast:mailbox"
    max_stream_length: int = 1000
    poll_interval: float = 2.0


@dataclass
class MailboxMessage:
    """Structured message exchanged between agents."""

    message_id: str
    sender: str
    recipient: str
    payload: Dict[str, Any]
    message_type: str = "direct_message"
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())

    def to_redis_fields(self) -> Dict[str, str]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": json.dumps(self.payload),
            "message_type": self.message_type,
            "timestamp": str(self.timestamp),
        }

    @classmethod
    def from_redis_fields(cls, fields: Dict[bytes, bytes]) -> "MailboxMessage":
        decoded = {k.decode(): v.decode() for k, v in fields.items()}
        payload = json.loads(decoded.get("payload", "{}"))
        return cls(
            message_id=decoded.get("message_id", str(uuid4())),
            sender=decoded.get("sender", "unknown"),
            recipient=decoded.get("recipient", "unknown"),
            payload=payload,
            message_type=decoded.get("message_type", "direct_message"),
            timestamp=float(decoded.get("timestamp", "0.0")),
        )


class RedisMailboxService:
    """Async Redis stream consumer/producer for inter-agent communication.
    
    This service manages bidirectional messaging using Redis Streams (XADD/XREADGROUP).
    Each agent has an inbox stream where other agents can send messages. Messages are
    consumed via consumer groups, providing at-least-once delivery with acknowledgment.
    
    Features:
        - Automatic consumer group creation and management
        - Message handler registration for inbound processing
        - Durable message queue with configurable retention
        - Async/await based for efficient concurrent operations
        - Automatic reconnection and error recovery
        
    Example:
        >>> config = MailboxConfig(host="localhost", db=0)
        >>> service = RedisMailboxService("my-agent", config)
        >>> 
        >>> # Register a handler for incoming messages
        >>> async def handle_message(msg: MailboxMessage):
        ...     print(f"Received: {msg.payload}")
        >>> service.register_handler(handle_message)
        >>> 
        >>> # Start consuming messages
        >>> await service.start()
        >>> 
        >>> # Send a message to another agent
        >>> await service.send_message("other-agent", {"text": "Hello!"})
        >>> 
        >>> # Graceful shutdown
        >>> await service.stop()
    """

    def __init__(self, agent_id: str, config: Optional[MailboxConfig] = None):
        """Initialize the mailbox service for a specific agent.
        
        Args:
            agent_id: Unique identifier for this agent instance
            config: Optional configuration (defaults to MailboxConfig())
            
        Note:
            The agent_id is used to generate unique inbox streams and consumer groups.
            Multiple service instances with the same agent_id will share the same inbox.
        """
        self.agent_id = agent_id
        self.config = config or MailboxConfig()
        self.logger = logging.getLogger(f"beast_mailbox.{agent_id}")
        self._client: Optional[redis.Redis] = None
        self._processing_task: Optional[asyncio.Task] = None
        self._handlers: List[Callable[[MailboxMessage], Awaitable[None]]] = []
        self._running = False
        self._consumer_group = f"{agent_id}:group"
        self._consumer_name = f"{agent_id}:{uuid4().hex[:6]}"

    @property
    def inbox_stream(self) -> str:
        """Get the Redis stream name for this agent's inbox.
        
        Returns:
            Fully qualified stream name in format: "{prefix}:{agent_id}:in"
            
        Example:
            For agent "alice" with prefix "beast:mailbox":
            Returns: "beast:mailbox:alice:in"
        """
        return f"{self.config.stream_prefix}:{self.agent_id}:in"

    async def connect(self) -> None:
        """Establish connection to Redis server and verify connectivity.
        
        Creates a Redis client if one doesn't exist and pings the server
        to ensure the connection is working.
        
        Raises:
            redis.exceptions.ConnectionError: If Redis server is unreachable
            redis.exceptions.AuthenticationError: If password is incorrect
            
        Note:
            This is idempotent - calling multiple times won't create multiple clients.
        """
        if self._client is None:
            self._client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                decode_responses=False,
            )
            # Ping to verify connection works
            await self._client.ping()

    async def start(self) -> bool:
        """Start the mailbox service and begin consuming messages.
        
        This method:
        1. Connects to Redis
        2. Creates the consumer group (if it doesn't exist)
        3. Launches the background message consumption loop
        
        Returns:
            True if service started successfully
            
        Raises:
            Exception: If consumer group creation fails (except BUSYGROUP)
            
        Note:
            The service runs in a background asyncio task. Messages are
            dispatched to registered handlers as they arrive.
        """
        await self.connect()
        assert self._client is not None
        try:
            await self._client.xgroup_create(
                name=self.inbox_stream,
                groupname=self._consumer_group,
                id="$",
                mkstream=True,
            )
            self.logger.info(
                "Created consumer group %s for stream %s",
                self._consumer_group,
                self.inbox_stream,
            )
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise
        self._running = True
        self._processing_task = asyncio.create_task(self._consume_loop())
        return True

    async def stop(self) -> None:
        """Gracefully stop the mailbox service and cleanup resources.
        
        This method:
        1. Sets _running flag to False (stops consume loop)
        2. Cancels and waits for the processing task to complete
        3. Closes the Redis client connection
        
        The method is idempotent and safe to call multiple times.
        Exceptions during shutdown are suppressed to ensure cleanup completes.
        
        Note:
            CancelledError is intentionally suppressed here since stop() IS
            the cleanup handler. Re-raising would propagate to callers
            expecting graceful shutdown.
        """
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:  # noqa: S7497
                # NOTE: SonarCloud flags this as python:S7497 (should re-raise)
                # However, stop() IS the cleanup handler - re-raising would propagate
                # to callers expecting graceful shutdown. This is intentional suppression.
                pass
            except Exception:
                pass  # Ignore other errors during shutdown
            finally:
                self._processing_task = None
        if self._client:
            await self._client.close()
            self._client = None

    def register_handler(self, handler: Callable[[MailboxMessage], Awaitable[None]]) -> None:
        """Register an async handler function for incoming messages.
        
        Args:
            handler: Async function that takes a MailboxMessage and returns None
            
        Example:
            >>> async def my_handler(msg: MailboxMessage):
            ...     print(f"Got: {msg.payload}")
            >>> service.register_handler(my_handler)
            
        Note:
            Multiple handlers can be registered. They are called sequentially
            for each message. Handler errors are caught and logged but don't
            stop other handlers from running.
        """
        self._handlers.append(handler)

    async def send_message(
        self,
        recipient: str,
        payload: Dict[str, Any],
        message_type: str = "direct_message",
        message_id: Optional[str] = None,
    ) -> str:
        """Send a message to another agent's inbox stream.
        
        Args:
            recipient: Agent ID of the message recipient
            payload: JSON-serializable data (dict, list, or primitives)
            message_type: Classification of the message (default: "direct_message")
            message_id: Optional custom message ID (auto-generated if None)
            
        Returns:
            Message ID of the sent message (useful for tracking/correlation)
            
        Raises:
            redis.exceptions.ConnectionError: If Redis connection fails
            
        Example:
            >>> msg_id = await service.send_message(
            ...     recipient="bob",
            ...     payload={"action": "ping", "data": [1, 2, 3]},
            ...     message_type="command"
            ... )
            
        Note:
            Messages are added to the recipient's inbox stream with MAXLEN
            to prevent unbounded growth. The stream will automatically trim
            old messages when the limit is reached.
        """
        await self.connect()
        assert self._client is not None
        message = MailboxMessage(
            message_id=message_id or str(uuid4()),
            sender=self.agent_id,
            recipient=recipient,
            payload=payload,
            message_type=message_type,
        )
        stream = f"{self.config.stream_prefix}:{recipient}:in"
        await self._client.xadd(
            stream,
            message.to_redis_fields(),
            maxlen=self.config.max_stream_length,
            approximate=True,
        )
        self.logger.debug("Sent message %s to stream %s", message.message_id, stream)
        return message.message_id

    async def _consume_loop(self) -> None:
        """Background loop that consumes messages from the inbox stream.
        
        This infinite loop:
        1. Reads messages from the consumer group using XREADGROUP
        2. Deserializes each message to a MailboxMessage
        3. Dispatches to all registered handlers
        4. Acknowledges processed messages with XACK
        
        The loop runs until _running is set to False (via stop() method).
        Errors are logged and the loop continues after a delay.
        
        Raises:
            asyncio.CancelledError: When the task is cancelled (propagated)
            
        Note:
            This method should not be called directly - it's launched
            automatically by start() as a background task.
        """
        assert self._client is not None
        while self._running:
            try:
                response = await self._client.xreadgroup(
                    groupname=self._consumer_group,
                    consumername=self._consumer_name,
                    streams={self.inbox_stream: ">"},
                    count=10,
                    block=int(self.config.poll_interval * 1000),
                )
                if not response:
                    continue
                for stream_name, messages in response:
                    self.logger.debug(
                        "Redis mailbox received %d messages from %s",
                        len(messages),
                        stream_name,
                    )
                    for message_id, fields in messages:
                        mailbox_message = MailboxMessage.from_redis_fields(fields)
                        await self._dispatch(mailbox_message)
                        await self._client.xack(stream_name, self._consumer_group, message_id)
            except asyncio.CancelledError:
                # Task cancelled - re-raise to propagate cancellation properly
                raise
            except Exception as exc:
                self.logger.exception("Error in mailbox consume loop: %s", exc)
                await asyncio.sleep(self.config.poll_interval)

    async def _dispatch(self, message: MailboxMessage) -> None:
        """Dispatch a message to all registered handlers.
        
        Args:
            message: The MailboxMessage to dispatch
            
        Behavior:
            - If no handlers are registered, logs the message and returns
            - Calls each handler sequentially
            - Handler exceptions are caught, logged, and don't affect other handlers
            
        Note:
            Handlers must not modify the handler list during iteration.
            Each handler is called with the same message instance.
        """
        if not self._handlers:
            self.logger.info("Mailbox message received with no handlers registered: %s", message)
            return
        # Iterate directly - handlers must not modify the list during iteration
        for handler in self._handlers:
            try:
                await handler(message)
            except Exception as exc:
                self.logger.exception("Mailbox handler failed: %s", exc)


"""High-level helper functions for Mix Python SDK that simplify common patterns.

This module provides ergonomic APIs for streaming interactions, wrapping the
lower-level Speakeasy-generated SDK with convenient patterns inspired by
modern Python SDKs.
"""

import asyncio
from typing import AsyncIterator, Callable, Optional, Any
from mix_python_sdk.models import (
    SSEThinkingEvent,
    SSEContentEvent,
    SSEToolEvent,
    SSEToolExecutionStartEvent,
    SSEToolExecutionCompleteEvent,
    SSECompleteEvent,
    SSEErrorEvent,
    SSEPermissionEvent,
    SessionData,
)


class StreamEvent:
    """Unified event wrapper for streaming responses."""

    def __init__(self, event_type: str, data: Any):
        self.type = event_type
        self.data = data

    @property
    def content(self) -> Optional[str]:
        """Get content text if this is a content event."""
        if self.type == "content" and hasattr(self.data, "content"):
            return self.data.content
        return None

    @property
    def thinking(self) -> Optional[str]:
        """Get thinking text if this is a thinking event."""
        if self.type == "thinking" and hasattr(self.data, "content"):
            return self.data.content
        return None

    @property
    def tool_name(self) -> Optional[str]:
        """Get tool name if this is a tool event."""
        if self.type == "tool" and hasattr(self.data, "name"):
            return self.data.name
        return None


async def query(
    mix,
    session_id: str,
    message: str,
) -> AsyncIterator[StreamEvent]:
    """Simple async iterator for streaming interactions.

    This is the simplest way to stream messages with Mix. It handles all the
    complexity of coordinating stream connection, message sending, and event
    processing.

    Args:
        mix: Mix SDK client instance
        session_id: Session ID to send the message to
        message: Message text to send

    Yields:
        StreamEvent objects with type and data

    Example:
        ```python
        async with Mix(server_url="http://localhost:8088") as mix:
            session = mix.sessions.create(title="Demo")

            async for event in query(mix, session.id, "Hello!"):
                if event.type == "content":
                    print(event.content, end="", flush=True)
                elif event.type == "thinking":
                    print(f"[thinking: {event.thinking}]")
        ```
    """
    stream_response = await mix.streaming.stream_events_async(session_id=session_id)
    await asyncio.sleep(0.5)  # Allow stream connection to establish

    # Start sending the message
    send_task = asyncio.create_task(
        mix.messages.send_async(id=session_id, text=message)
    )

    async with stream_response.result as event_stream:
        async for event in event_stream:
            if isinstance(event, SSEThinkingEvent):
                yield StreamEvent("thinking", event.data)
            elif isinstance(event, SSEContentEvent):
                yield StreamEvent("content", event.data)
            elif isinstance(event, SSEToolEvent):
                yield StreamEvent("tool", event.data)
            elif isinstance(event, SSEToolExecutionStartEvent):
                yield StreamEvent("tool_execution_start", event.data)
            elif isinstance(event, SSEToolExecutionCompleteEvent):
                yield StreamEvent("tool_execution_complete", event.data)
            elif isinstance(event, SSEErrorEvent):
                yield StreamEvent("error", event.data)
            elif isinstance(event, SSEPermissionEvent):
                yield StreamEvent("permission", event.data)
            elif isinstance(event, SSECompleteEvent):
                yield StreamEvent("complete", event.data)
                break

    # Wait for send to complete if not already done
    await send_task


async def send_with_callbacks(
    mix,
    session_id: str,
    message: str,
    *,
    on_thinking: Optional[Callable[[str], None]] = None,
    on_content: Optional[Callable[[str], None]] = None,
    on_tool: Optional[Callable[[Any], None]] = None,
    on_tool_execution_start: Optional[Callable[[Any], None]] = None,
    on_tool_execution_complete: Optional[Callable[[Any], None]] = None,
    on_error: Optional[Callable[[str], None]] = None,
    on_permission: Optional[Callable[[Any], None]] = None,
    on_complete: Optional[Callable[[], None]] = None,
) -> None:
    """Send a message and process streaming events with callbacks.

    This is the most ergonomic way to handle streaming responses. Provide
    callback functions for the events you care about, and this function
    handles all the complexity.

    Args:
        mix: Mix SDK client instance
        session_id: Session ID to send the message to
        message: Message text to send
        on_thinking: Callback for thinking events (receives thinking text)
        on_content: Callback for content events (receives content text)
        on_tool: Callback for tool events (receives tool data)
        on_tool_execution_start: Callback for tool execution start events
        on_tool_execution_complete: Callback for tool execution complete events
        on_error: Callback for error events (receives error message)
        on_permission: Callback for permission events (receives permission data)
        on_complete: Callback when stream completes

    Example:
        ```python
        await send_with_callbacks(
            mix,
            session_id=session.id,
            message="What's the weather?",
            on_thinking=lambda text: print(f"🤔 {text}", end="", flush=True),
            on_content=lambda text: print(f"💬 {text}", end="", flush=True),
            on_tool=lambda tool: print(f"\\n🔧 Using {tool.name}"),
            on_complete=lambda: print("\\n✅ Done!")
        )
        ```
    """
    stream_response = await mix.streaming.stream_events_async(session_id=session_id)
    await asyncio.sleep(0.5)  # Allow stream connection to establish

    async with stream_response.result as event_stream:

        async def process_events():
            async for event in event_stream:
                if isinstance(event, SSEThinkingEvent) and on_thinking:
                    on_thinking(event.data.content)
                elif isinstance(event, SSEContentEvent) and on_content:
                    on_content(event.data.content)
                elif isinstance(event, SSEToolEvent) and on_tool:
                    on_tool(event.data)
                elif (
                    isinstance(event, SSEToolExecutionStartEvent)
                    and on_tool_execution_start
                ):
                    on_tool_execution_start(event.data)
                elif (
                    isinstance(event, SSEToolExecutionCompleteEvent)
                    and on_tool_execution_complete
                ):
                    on_tool_execution_complete(event.data)
                elif isinstance(event, SSEErrorEvent):
                    if on_error:
                        on_error(event.data.error)
                    break
                elif isinstance(event, SSEPermissionEvent) and on_permission:
                    on_permission(event.data)
                elif isinstance(event, SSECompleteEvent):
                    if on_complete:
                        on_complete()
                    break

        await asyncio.gather(
            mix.messages.send_async(id=session_id, text=message),
            process_events(),
        )


class StreamingSession:
    """Context manager for streaming sessions with automatic lifecycle management.

    This provides the most convenient way to work with sessions by automatically
    handling session creation, cleanup, and streaming in one unified interface.

    Example:
        ```python
        async with Mix(server_url="http://localhost:8088") as mix:
            mix.authentication.store_api_key(api_key=api_key, provider="openrouter")

            async with StreamingSession(mix, title="Demo") as session:
                await session.send(
                    "Hello!",
                    on_content=lambda text: print(text, end="", flush=True),
                    on_complete=lambda: print("\\nDone!")
                )
        ```
    """

    def __init__(
        self,
        mix,
        title: str,
        custom_system_prompt: Optional[str] = None,
    ):
        """Initialize a streaming session.

        Args:
            mix: Mix SDK client instance
            title: Title for the session
            custom_system_prompt: Optional custom system prompt
        """
        self.mix = mix
        self.title = title
        self.custom_system_prompt = custom_system_prompt
        self._session: Optional[SessionData] = None

    async def __aenter__(self):
        """Create the session when entering context."""
        self._session = self.mix.sessions.create(
            title=self.title,
            custom_system_prompt=self.custom_system_prompt,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Delete the session when exiting context."""
        if self._session:
            self.mix.sessions.delete(id=self._session.id)

    @property
    def id(self) -> str:
        """Get the session ID."""
        if not self._session:
            raise RuntimeError("Session not created. Use 'async with' context manager.")
        return self._session.id

    @property
    def session(self) -> SessionData:
        """Get the session data."""
        if not self._session:
            raise RuntimeError("Session not created. Use 'async with' context manager.")
        return self._session

    async def query(self, message: str) -> AsyncIterator[StreamEvent]:
        """Send a message and iterate over events.

        Args:
            message: Message text to send

        Yields:
            StreamEvent objects
        """
        async for event in query(self.mix, self.id, message):
            yield event

    async def send(
        self,
        message: str,
        *,
        on_thinking: Optional[Callable[[str], None]] = None,
        on_content: Optional[Callable[[str], None]] = None,
        on_tool: Optional[Callable[[Any], None]] = None,
        on_tool_execution_start: Optional[Callable[[Any], None]] = None,
        on_tool_execution_complete: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_permission: Optional[Callable[[Any], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        """Send a message with callback-based event handling.

        Args:
            message: Message text to send
            on_thinking: Callback for thinking events
            on_content: Callback for content events
            on_tool: Callback for tool events
            on_tool_execution_start: Callback for tool execution start events
            on_tool_execution_complete: Callback for tool execution complete events
            on_error: Callback for error events
            on_permission: Callback for permission events
            on_complete: Callback when stream completes
        """
        await send_with_callbacks(
            self.mix,
            self.id,
            message,
            on_thinking=on_thinking,
            on_content=on_content,
            on_tool=on_tool,
            on_tool_execution_start=on_tool_execution_start,
            on_tool_execution_complete=on_tool_execution_complete,
            on_error=on_error,
            on_permission=on_permission,
            on_complete=on_complete,
        )

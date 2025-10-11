"""Factory functions for creating LangGraph adapters and handlers.

This module provides convenient factory functions for creating adapters
and handlers without exposing the internal adapter implementation details.
"""

import json
from collections.abc import AsyncGenerator, Callable
from typing import Any

from ..crew import Crew
from .adapter import LangGraphAdapter
from .protocol import TaskInput, StreamMessage


def create_sse_handler(
    crew: Crew,
) -> Callable[[TaskInput], AsyncGenerator[str, None]]:
    """Create a simple SSE handler for integration with custom servers.

    Args:
        crew: LangCrew Crew instance

    Returns:
        Async function that accepts TaskInput and yields SSE strings

    Example:
        from langcrew.web import create_sse_handler

        # Create SSE handler
        sse_handler = create_sse_handler(crew)

        # Use in your FastAPI/Flask app
        @app.post("/chat")
        async def chat(request: dict):
            task_input = TaskInput(
                session_id=request.get("session_id"),
                message=request.get("content")
            )

            return StreamingResponse(
                sse_handler(task_input),
                media_type="text/event-stream"
            )
    """
    adapter = LangGraphAdapter(crew)
    return adapter.execute


def create_message_generator(
    crew: Crew,
) -> Callable[[TaskInput], AsyncGenerator[StreamMessage, None]]:
    """Create a message generator for direct integration without SSE formatting.

    Args:
        crew: LangCrew Crew instance

    Returns:
        Async function that yields StreamMessage objects

    Example:
        from langcrew.web import create_message_generator

        # Create message generator
        message_gen = create_message_generator(crew)

        # Use in your custom implementation
        async for message in message_gen(task_input):
            # Process message as needed
            await websocket.send(message.model_dump_json())
    """
    adapter = LangGraphAdapter(crew)

    async def generate_messages(task_input: TaskInput):
        """Generate StreamMessage objects without SSE formatting."""
        async for sse_chunk in adapter.execute(task_input):
            # Parse SSE format back to message
            if sse_chunk.startswith("data: "):
                message_data = json.loads(sse_chunk[6:].strip())
                yield StreamMessage(**message_data)

    return generate_messages

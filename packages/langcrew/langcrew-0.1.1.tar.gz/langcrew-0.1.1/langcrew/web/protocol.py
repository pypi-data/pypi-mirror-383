"""
Protocol definitions for Adapter SDK
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel


class MessageType(str, Enum):
    """Frontend message types - Common component types"""

    ERROR = "error"  # Reserved for error handling

    CONFIG = "config"
    LIVE_STATUS = "live_status"

    SESSION_INIT = "session_init"  # Session initialization message
    FINISH_REASON = "finish_reason"  # Finish reason

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MARKDOWN = "markdown"

    MESSAGE_STREAM = "message_stream"
    MESSAGE_RESULT = "message_result"

    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

    PLAN = "plan"

    MESSAGE_TO_USER = "message_to_user"

    # HITL related message types
    USER_INPUT = "user_input"  # User input request
    TOOL_APPROVAL_REQUEST = "tool_approval_request"  # Tool approval request


# Stream message protocol
class StreamMessage(BaseModel):
    """Stream message base structure for all streaming scenarios"""

    id: str
    role: str = "assistant"  # Unified default value
    type: MessageType
    content: str
    detail: dict[str, Any] | None = None
    timestamp: int
    session_id: str | None = None
    task_id: str | None = None  # Task identifier for precise control and tracking
    trace_id: str | None = None


class TaskExecutionStatus(str, Enum):
    """Task execution status for finish signals"""

    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    USER_INPUT = "user_input"  # Waiting for user input


class StepStatus(str, Enum):
    """Step status"""

    PENDING = "pending"
    RUNNING = "running"  # Step is currently running
    SUCCESS = "success"  # Step completed successfully
    FAILED = "failed"


class ToolResult(str, Enum):
    """Tool execution result"""

    PENDING = "pending"  # Tool call initiated, waiting for execution
    SUCCESS = "success"  # Tool execution completed successfully
    FAILED = "failed"  # Tool execution failed


# Internal data structures
class TaskInput(BaseModel):
    """Unified task input for both new conversations and resume scenarios

    ID descriptions:
    - session_id: Session identifier for maintaining multi-turn conversation context, also used as LangGraph's thread_id
    - user_id: User identifier for personalization (optional)
    """

    message: str
    session_id: str  # Required for multi-turn conversations and context continuity
    user_id: str | None = None  # User identifier for personalization (optional)
    language: str | None = None  # Language field for tool display
    interrupt_data: dict[str, Any] | None = None  # Interrupt data for resume scenarios

    @property
    def is_resume(self) -> bool:
        """Whether this is resuming an interrupted execution"""
        return self.interrupt_data is not None

    def __init__(self, **data):
        # Ensure session_id is provided
        if "session_id" not in data or not data["session_id"]:
            raise ValueError("session_id is required for TaskInput")
        super().__init__(**data)


# API protocol classes
class ChatRequest(BaseModel):
    """Chat request for unified chat API"""

    message: str
    session_id: str | None = None
    user_id: str | None = None  # User identifier for personalization (optional)
    language: str | None = None  # Language preference for tool display and responses
    interrupt_data: dict[str, Any] | None = None  # For resume scenarios


class StopRequest(BaseModel):
    """Stop request for stopping chat execution"""

    session_id: str
    reason: str = "User stopped"

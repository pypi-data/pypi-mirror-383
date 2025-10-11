import logging
from typing import Any, ClassVar

from langchain_core.runnables import RunnableConfig, ensure_config

logger = logging.getLogger(__name__)


class RunnableStateManager:
    """Utility class for managing state in RunnableConfig.

    IMPORTANT: This state manager must be initialized at the top-level LangGraph
    before being used in any nested runnables or agents. The state is stored in
    the RunnableConfig metadata and persists throughout the execution chain.
    """

    METADATA_KEY: ClassVar[str] = "metadata"
    RUNNABLE_CONFIG_STATE_KEY: ClassVar[str] = "_langcrew_runnable_config_state_"

    @classmethod
    def init_state(cls, config: RunnableConfig) -> dict[str, Any]:
        """Initialize the state for the specified session.

        MUST be called at the top-level LangGraph before any other state operations.
        This ensures the state container is properly set up in the RunnableConfig metadata.
        """
        assert config is not None, "config is required"
        if cls.METADATA_KEY not in config:
            config[cls.METADATA_KEY] = {}
        if cls.RUNNABLE_CONFIG_STATE_KEY not in config[cls.METADATA_KEY]:
            config[cls.METADATA_KEY][cls.RUNNABLE_CONFIG_STATE_KEY] = {}
        return config[cls.METADATA_KEY][cls.RUNNABLE_CONFIG_STATE_KEY]

    @classmethod
    def _get_internal_state(
        cls, config: RunnableConfig | None = None
    ) -> dict[str, Any]:
        config = cls._context_ensure_config(config)
        """Get the metadata for specified session."""
        metadata = config.get(cls.METADATA_KEY, {})
        state = metadata.get(cls.RUNNABLE_CONFIG_STATE_KEY, None)
        if state is None:
            logger.warning("State not initialized. Call init_state() first.")
        return state

    @classmethod
    def get_state(cls, config: RunnableConfig | None = None) -> dict[str, Any]:
        config = cls._context_ensure_config(config)
        """Get the current state for specified session."""
        state = cls._get_internal_state(config)
        return state.copy() if state else None

    @classmethod
    def update_state(
        cls, updates: dict[str, Any], config: RunnableConfig | None = None
    ) -> None:
        config = cls._context_ensure_config(config)
        """Update the state with new values for specified session."""
        state = cls._get_internal_state(config)
        if state is None:
            return
        state.update(updates)

    @classmethod
    def get_value(
        cls, key: str, default: Any = None, config: RunnableConfig | None = None
    ) -> Any:
        config = cls._context_ensure_config(config)
        """Get a specific value from state for specified session."""
        state = cls._get_internal_state(config)
        if state is None:
            return None
        return state.get(key, default)

    @classmethod
    def set_value(
        cls, key: str, value: Any, config: RunnableConfig | None = None
    ) -> None:
        config = cls._context_ensure_config(config)
        """Set a specific value in state for specified session."""
        state = cls._get_internal_state(config)
        if state is None:
            return
        state[key] = value

    @classmethod
    def del_key(cls, key: str, config: RunnableConfig | None = None) -> None:
        config = cls._context_ensure_config(config)
        """Delete a specific key from state for specified session."""
        state = cls._get_internal_state(config)
        if state is None:
            return
        if key in state:
            del state[key]

    @classmethod
    def has_key(cls, key: str, config: RunnableConfig | None = None) -> bool:
        """Check if a key exists in state for specified session."""
        config = cls._context_ensure_config(config)
        state = cls._get_internal_state(config)
        if state is None:
            return False
        return key in state

    @classmethod
    def _context_ensure_config(cls, config: RunnableConfig | None) -> RunnableConfig:
        """Ensure the config is not None."""
        return config or ensure_config()

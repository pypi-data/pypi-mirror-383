from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator, Optional

from abvdev._client.client import ABV
from abvdev._client.resource_manager import ABVResourceManager
from abvdev.logger import abv_logger

# Context variable to track the current abv_api_key in execution context
_current_api_key: ContextVar[Optional[str]] = ContextVar(
    "abv_api_key", default=None
)


@contextmanager
def _set_current_api_key(api_key: Optional[str]) -> Iterator[None]:
    """Context manager to set and restore the current API key in execution context.

    Args:
        api_key: The API key to set in context. If None, context is not modified.

    Yields:
        None
    """
    if api_key is None:
        yield  # Don't modify context if no key provided
        return

    token = _current_api_key.set(api_key)
    try:
        yield
    finally:
        _current_api_key.reset(token)


def get_client(*, api_key: Optional[str] = None) -> ABV:
    """Get or create a ABV client instance.

    Returns an existing ABV client or creates a new one if none exists. In multi-project setups,
    providing an api_key is required. Multi-project support is experimental - see ABV docs.

    Behavior:
    - Single project: Returns existing client or creates new one
    - Multi-project: Requires api_key to return specific client
    - No api_key in multi-project: Returns disabled client to prevent data leakage

    The function uses a singleton pattern per api_key to conserve resources and maintain state.

    Args:
        api_key (Optional[str]): Project identifier
            - With key: Returns client for that project
            - Without key: Returns single client or disabled client if multiple exist

    Returns:
        ABV: Client instance in one of three states:
            1. Client for specified api_key
            2. Default client for single-project setup
            3. Disabled client when multiple projects exist without key

    Security:
        Disables tracing when multiple projects exist without explicit key to prevent
        cross-project data leakage. Multi-project setups are experimental.

    Example:
        ```python
        # Single project
        client = get_client()  # Default client

        # In multi-project usage:
        client_a = get_client(api_key="project_a_key")  # Returns project A's client
        client_b = get_client(api_key="project_b_key")  # Returns project B's client

        # Without specific key in multi-project setup:
        client = get_client()  # Returns disabled client for safety
        ```
    """
    with ABVResourceManager._lock:
        active_instances = ABVResourceManager._instances

        # If no explicit api_key provided, check execution context
        if not api_key:
            api_key = _current_api_key.get(None)

        if not api_key:
            if len(active_instances) == 0:
                # No clients initialized yet, create default instance
                return ABV()

            if len(active_instances) == 1:
                # Only one client exists, safe to use without specifying key
                instance = list(active_instances.values())[0]

                # Initialize with the credentials bound to the instance
                # This is important if the original instance was instantiated
                # via constructor arguments
                return ABV(
                    api_key=instance.api_key,
                    host=instance.host,
                    tracing_enabled=instance.tracing_enabled,
                )

            else:
                # Multiple clients exist but no key specified - disable tracing
                # to prevent cross-project data leakage
                abv_logger.warning(
                    "No 'abv_api_key' passed to decorated function, but multiple abv clients are instantiated in current process. Skipping tracing for this function to avoid cross-project leakage."
                )
                return ABV(
                    tracing_enabled=False, api_key="fake"
                )

        else:
            # Specific key provided, look up existing instance
            target_instance: Optional[ABVResourceManager] = active_instances.get(
                api_key, None
            )

            if target_instance is None:
                # No instance found with this key - client not initialized properly
                abv_logger.warning(
                    f"No ABV client with API key {api_key[:8]}... has been initialized. Skipping tracing for decorated function."
                )
                return ABV(
                    tracing_enabled=False, api_key="fake"
                )

            # target_instance is guaranteed to be not None at this point
            return ABV(
                api_key=api_key,
                host=target_instance.host,
                tracing_enabled=target_instance.tracing_enabled,
            )

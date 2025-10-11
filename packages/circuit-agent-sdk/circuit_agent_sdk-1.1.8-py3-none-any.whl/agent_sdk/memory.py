"""
Memory operations for agent session storage.

This module provides the MemoryApi class for storing and retrieving key-value
pairs scoped to the current agent session.
"""

from typing import TYPE_CHECKING

from .types.memory import (
    MemoryDeleteData,
    MemoryDeleteResponse,
    MemoryGetData,
    MemoryGetResponse,
    MemoryListData,
    MemoryListResponse,
    MemorySetData,
    MemorySetResponse,
)

if TYPE_CHECKING:
    from .agent_sdk import AgentSdk


class MemoryApi:
    """
    Session-scoped key-value storage operations.

    All keys are automatically namespaced by agentId and sessionId, providing
    isolated storage for each agent session. Perfect for maintaining state
    across execution cycles.
    """

    def __init__(self, sdk: "AgentSdk"):
        self._sdk = sdk

    def set(self, key: str, value: str) -> MemorySetResponse:
        """
        Set a key-value pair in session memory.

        Store a string value with a unique key. The key is automatically scoped to your
        agent and session, so you don't need to worry about collisions.

        **Input**: `key: str, value: str`
            - `key` (str): Unique identifier for the value (1-255 characters)
            - `value` (str): String value to store

        **Output**: `MemorySetResponse`
            - `success` (bool): Whether the operation succeeded
            - `data` (MemorySetData | None): Present on success
                - `key` (str): The key that was set
            - `error` (str | None): Error message on failure
            - `errorDetails` (dict | None): Detailed error info on failure

        **Key Functionality**:
            - Automatic namespacing by agentId and sessionId
            - Overwrites existing values if key already exists
            - Persistent across agent execution cycles

        **Example**:
            ```python
            # Store user preferences
            result = sdk.memory.set("lastSwapNetwork", "ethereum:42161")

            if result.success and result.data:
                print(f"Stored key: {result.data.key}")
            else:
                print(f"Failed to store: {result.error}")
            ```

        **Success Case**:
            ```python
            {
                "success": True,
                "data": {"key": "lastSwapNetwork"},
                "error": None,
                "errorDetails": None
            }
            ```

        **Error Case**:
            ```python
            {
                "success": False,
                "data": None,
                "error": "Failed to set memory",
                "errorDetails": {"message": "Connection failed", "status": 500}
            }
            ```

        Args:
            key: Unique identifier for the value
            value: String value to store

        Returns:
            MemorySetResponse: Wrapped response with success status and key
        """
        return self._handle_memory_set(key, value)

    def get(self, key: str) -> MemoryGetResponse:
        """
        Get a value by key from session memory.

        Retrieve a previously stored value. Returns an error if the key doesn't exist.

        **Input**: `key: str`
            - `key` (str): The key to retrieve

        **Output**: `MemoryGetResponse`
            - `success` (bool): Whether the operation succeeded
            - `data` (MemoryGetData | None): Present on success
                - `key` (str): The requested key
                - `value` (str): The stored value
            - `error` (str | None): Error message (e.g., "Key not found")
            - `errorDetails` (dict | None): Detailed error info on failure

        **Key Functionality**:
            - Retrieves values stored with set()
            - Returns error if key doesn't exist
            - Automatic namespace resolution

        **Example**:
            ```python
            # Retrieve stored preferences
            result = sdk.memory.get("lastSwapNetwork")

            if result.success and result.data:
                print(f"Network: {result.data.value}")
            else:
                print(f"Key not found: {result.error}")
            ```

        **Success Case**:
            ```python
            {
                "success": True,
                "data": {
                    "key": "lastSwapNetwork",
                    "value": "ethereum:42161"
                },
                "error": None,
                "errorDetails": None
            }
            ```

        **Error Case (Key Not Found)**:
            ```python
            {
                "success": False,
                "data": None,
                "error": "Key not found",
                "errorDetails": {"message": "Key not found", "status": 404}
            }
            ```

        Args:
            key: The key to retrieve

        Returns:
            MemoryGetResponse: Wrapped response with key and value, or error details
        """
        return self._handle_memory_get(key)

    def delete(self, key: str) -> MemoryDeleteResponse:
        """
        Delete a key from session memory.

        Remove a key-value pair. Succeeds even if the key doesn't exist.

        **Input**: `key: str`
            - `key` (str): The key to delete

        **Output**: `MemoryDeleteResponse`
            - `success` (bool): Whether the operation succeeded
            - `data` (MemoryDeleteData | None): Present on success
                - `key` (str): The key that was deleted
            - `error` (str | None): Error message on failure
            - `errorDetails` (dict | None): Detailed error info on failure

        **Key Functionality**:
            - Removes key-value pair from storage
            - Idempotent - succeeds even if key doesn't exist
            - Frees up storage space

        **Example**:
            ```python
            # Clean up temporary data
            result = sdk.memory.delete("tempSwapQuote")

            if result.success and result.data:
                print(f"Deleted key: {result.data.key}")
            ```

        **Success Case**:
            ```python
            {
                "success": True,
                "data": {"key": "tempSwapQuote"},
                "error": None,
                "errorDetails": None
            }
            ```

        **Error Case**:
            ```python
            {
                "success": False,
                "data": None,
                "error": "Failed to delete memory",
                "errorDetails": {"message": "Connection failed", "status": 500}
            }
            ```

        Args:
            key: The key to delete

        Returns:
            MemoryDeleteResponse: Wrapped response with success status and deleted key
        """
        return self._handle_memory_delete(key)

    def list(self) -> MemoryListResponse:
        """
        List all keys in session memory.

        Get an array of all keys stored for this agent session. Useful for debugging
        or iterating through stored data.

        **Input**: None

        **Output**: `MemoryListResponse`
            - `success` (bool): Whether the operation succeeded
            - `data` (MemoryListData | None): Present on success
                - `keys` (list[str]): Array of all stored keys
                - `count` (int): Number of keys
            - `error` (str | None): Error message on failure
            - `errorDetails` (dict | None): Detailed error info on failure

        **Key Functionality**:
            - Returns all keys in current session
            - Empty list if no keys stored
            - Useful for cleanup or iteration

        **Example**:
            ```python
            # List all stored keys
            result = sdk.memory.list()

            if result.success and result.data:
                print(f"Found {result.data.count} keys:")
                for key in result.data.keys:
                    print(f"  - {key}")
            ```

        **Success Case (With Keys)**:
            ```python
            {
                "success": True,
                "data": {
                    "keys": ["lastSwapNetwork", "userPreferences", "sessionData"],
                    "count": 3
                },
                "error": None,
                "errorDetails": None
            }
            ```

        **Success Case (No Keys)**:
            ```python
            {
                "success": True,
                "data": {
                    "keys": [],
                    "count": 0
                },
                "error": None,
                "errorDetails": None
            }
            ```

        **Error Case**:
            ```python
            {
                "success": False,
                "data": None,
                "error": "Failed to list memory keys",
                "errorDetails": {"message": "Connection failed", "status": 500}
            }
            ```

        Returns:
            MemoryListResponse: Wrapped response with array of keys and count
        """
        return self._handle_memory_list()

    def _handle_memory_set(self, key: str, value: str) -> MemorySetResponse:
        """Handle memory set requests."""
        self._sdk._log("=== MEMORY SET ===")
        self._sdk._log("Key:", key)
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("==================")

        try:
            if self._sdk.config.testing:
                return MemorySetResponse(
                    success=True,
                    data=MemorySetData(key=key),
                    error=None,
                    errorDetails=None,
                )

            response = self._sdk.client.post(f"/v1/memory/{key}", {"value": value})

            return MemorySetResponse(
                success=True,
                data=MemorySetData(**response),
                error=None,
                errorDetails=None,
            )
        except Exception as error:
            self._sdk._log("=== MEMORY SET ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("========================")

            error_message = "Failed to set memory"
            status = None
            status_text = None

            if isinstance(error, Exception):
                error_message = str(error)

                # Try to extract HTTP status from error message
                if hasattr(error, "response") and hasattr(
                    error.response, "status_code"
                ):
                    status = error.response.status_code
                    if hasattr(error.response, "reason"):
                        status_text = str(error.response.reason)

            return MemorySetResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )

    def _handle_memory_get(self, key: str) -> MemoryGetResponse:
        """Handle memory get requests."""
        self._sdk._log("=== MEMORY GET ===")
        self._sdk._log("Key:", key)
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("==================")

        try:
            if self._sdk.config.testing:
                return MemoryGetResponse(
                    success=True,
                    data=MemoryGetData(key=key, value="test-value"),
                    error=None,
                    errorDetails=None,
                )

            response = self._sdk.client.get(f"/v1/memory/{key}")

            return MemoryGetResponse(
                success=True,
                data=MemoryGetData(**response),
                error=None,
                errorDetails=None,
            )
        except Exception as error:
            self._sdk._log("=== MEMORY GET ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("========================")

            error_message = "Failed to get memory"
            status = None
            status_text = None

            if isinstance(error, Exception):
                error_message = str(error)

                # Try to extract HTTP status from error message
                if hasattr(error, "response") and hasattr(
                    error.response, "status_code"
                ):
                    status = error.response.status_code
                    if hasattr(error.response, "reason"):
                        status_text = str(error.response.reason)

            return MemoryGetResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )

    def _handle_memory_delete(self, key: str) -> MemoryDeleteResponse:
        """Handle memory delete requests."""
        self._sdk._log("=== MEMORY DELETE ===")
        self._sdk._log("Key:", key)
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("=====================")

        try:
            if self._sdk.config.testing:
                return MemoryDeleteResponse(
                    success=True,
                    data=MemoryDeleteData(key=key),
                    error=None,
                    errorDetails=None,
                )

            response = self._sdk.client.delete(f"/v1/memory/{key}")

            return MemoryDeleteResponse(
                success=True,
                data=MemoryDeleteData(**response),
                error=None,
                errorDetails=None,
            )
        except Exception as error:
            self._sdk._log("=== MEMORY DELETE ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("===========================")

            error_message = "Failed to delete memory"
            status = None
            status_text = None

            if isinstance(error, Exception):
                error_message = str(error)

                # Try to extract HTTP status from error message
                if hasattr(error, "response") and hasattr(
                    error.response, "status_code"
                ):
                    status = error.response.status_code
                    if hasattr(error.response, "reason"):
                        status_text = str(error.response.reason)

            return MemoryDeleteResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )

    def _handle_memory_list(self) -> MemoryListResponse:
        """Handle memory list requests."""
        self._sdk._log("=== MEMORY LIST ===")
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("===================")

        try:
            if self._sdk.config.testing:
                return MemoryListResponse(
                    success=True,
                    data=MemoryListData(keys=[], count=0),
                    error=None,
                    errorDetails=None,
                )

            response = self._sdk.client.get("/v1/memory/list")

            return MemoryListResponse(
                success=True,
                data=MemoryListData(**response),
                error=None,
                errorDetails=None,
            )
        except Exception as error:
            self._sdk._log("=== MEMORY LIST ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("=========================")

            error_message = "Failed to list memory keys"
            status = None
            status_text = None

            if isinstance(error, Exception):
                error_message = str(error)

                # Try to extract HTTP status from error message
                if hasattr(error, "response") and hasattr(
                    error.response, "status_code"
                ):
                    status = error.response.status_code
                    if hasattr(error.response, "reason"):
                        status_text = str(error.response.reason)

            return MemoryListResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )

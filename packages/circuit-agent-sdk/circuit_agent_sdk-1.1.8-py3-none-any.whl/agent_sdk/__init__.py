"""
Circuit Agent Python SDK — clean, type-safe agent automation.

- `AgentSdk` — main class with `send_log()` and `sign_and_send()`
- `AgentUtils` — utilities available via `AgentSdk(...).utils`
- Types & guards — networks, requests, responses

Install: `pip install circuit-agent-sdk`

Minimal example:
```python
from agent_sdk import AgentSdk, SDKConfig

sdk = AgentSdk(SDKConfig(session_id=123))
sdk.send_log({"type": "observe", "short_message": "Hello"})
```

Features:
- 🎯 Simple API: Core methods - `send_log()`, `sign_and_send()`, `sign_message()`
- 🔒 Type Safety: Network parameter determines valid request shapes automatically
- 🚀 Cross-Chain: Unified interface for EVM and Solana networks
- 🌉 Swidge: Cross-chain swaps via `sdk.swidge.quote()` and `sdk.swidge.execute()`
- 📈 Polymarket: Prediction markets via `sdk.polymarket.positions()`, `market_order()`, `redeem_positions()`
- 💾 Memory: Session-scoped key-value storage via `sdk.memory.set()`, `get()`, `delete()`, `list()`
- 📦 Utilities: Helper functions for common operations
- 🛠️ HTTP Server: Agent wrapper for local/worker deployment

For more information, see the README.md file or visit:
https://github.com/circuitorg/agent-sdk-python
"""

# Main SDK exports
# Agent wrapper for local/worker deployment
from .agent import (
    Agent,
    AgentConfig,
    AgentRequest,
    AgentResponse,
    ChatFunctionContract,
    ExecutionFunctionContract,
    HealthCheckFunctionContract,
    HealthResponse,
    StopFunctionContract,
    create_agent_handler,
)
from .agent_sdk import AgentSdk

# Core types
from .types import (
    AddLogRequest,
    MemoryDeleteRequest,
    MemoryDeleteResponse,
    MemoryGetRequest,
    MemoryGetResponse,
    MemoryListRequest,
    MemoryListResponse,
    MemorySetRequest,
    MemorySetResponse,
    Network,
    SDKConfig,
    SignAndSendRequest,
    SignAndSendResponse,
    get_chain_id_from_network,
    is_ethereum_network,
    is_solana_network,
)

# Utility functions
from .utils import get_agent_config_from_pyproject, setup_logging

__all__ = [
    # Main SDK
    "AgentSdk",
    # Agent wrapper for HTTP server deployment
    "Agent",
    "AgentConfig",
    "AgentRequest",
    "AgentResponse",
    "HealthResponse",
    "create_agent_handler",
    "ExecutionFunctionContract",
    "StopFunctionContract",
    "ChatFunctionContract",
    "HealthCheckFunctionContract",
    # Core types
    "Network",
    "SDKConfig",
    "AddLogRequest",
    "SignAndSendRequest",
    "SignAndSendResponse",
    # Memory types
    "MemorySetRequest",
    "MemoryGetRequest",
    "MemoryDeleteRequest",
    "MemoryListRequest",
    "MemorySetResponse",
    "MemoryGetResponse",
    "MemoryDeleteResponse",
    "MemoryListResponse",
    # Network detection utilities
    "is_ethereum_network",
    "is_solana_network",
    "get_chain_id_from_network",
    # Utility functions
    "get_agent_config_from_pyproject",
    "setup_logging",
]

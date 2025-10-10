"""
Transport Layer for OpenAgents.

This package provides transport implementations for agent communication.
Includes WebSocket, gRPC, and base transport abstractions.
"""

# Import base classes
from .base import Transport, Message

# Import transport implementations
from .websocket import WebSocketTransport, create_websocket_transport
from .grpc import GRPCTransport, OpenAgentsGRPCServicer, create_grpc_transport
from .http import HttpTransport

# Import transport types and models
from openagents.models.transport import (
    TransportType,
    ConnectionState,
    PeerMetadata,
    ConnectionInfo,
    AgentConnection,
)
from openagents.models.event import Event

# Simplified exports - only working transports
__all__ = [
    # Base classes
    "Transport",
    "Message",
    "Event",
    # Transport implementations
    "WebSocketTransport",
    "GRPCTransport",
    "HttpTransport",
    "OpenAgentsGRPCServicer",
    # Convenience functions
    "create_websocket_transport",
    "create_grpc_transport",
    # Transport types and models
    "TransportType",
    "ConnectionState",
    "PeerMetadata",
    "ConnectionInfo",
    "AgentConnection",
]

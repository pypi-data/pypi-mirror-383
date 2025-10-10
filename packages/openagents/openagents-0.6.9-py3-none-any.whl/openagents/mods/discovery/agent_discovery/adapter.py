"""
Agent-level agent discovery protocol for OpenAgents.

This protocol allows agents to announce their capabilities to the network
and for other agents to discover agents with specific capabilities.
"""

from typing import Dict, Any, Optional, List
import logging
from openagents.core.base_mod_adapter import BaseModAdapter
from openagents.models.messages import Event, EventNames
from openagents.models.tool import AgentTool
from openagents.utils.message_util import get_mod_event_thread_id
import copy

logger = logging.getLogger(__name__)

# Protocol constants
PROTOCOL_NAME = "openagents.mods.discovery.agent_discovery"
ANNOUNCE_CAPABILITIES = "announce_capabilities"
DISCOVER_AGENTS = "discover_agents"


class AgentDiscoveryAdapter(BaseModAdapter):
    """Agent adapter for the agent discovery protocol.

    This adapter allows agents to announce their capabilities and
    discover other agents with specific capabilities.
    """

    def __init__(self):
        """Initialize the agent discovery adapter."""
        super().__init__(PROTOCOL_NAME)
        self._capabilities = {}

    def initialize(self) -> bool:
        """Initialize the mod adapter.

        Returns:
            bool: True if initialization was successful
        """
        logger.info(f"Initializing {self.mod_name} adapter for agent {self.agent_id}")
        return True

    def shutdown(self) -> bool:
        """Shutdown the mod adapter gracefully.

        Returns:
            bool: True if shutdown was successful
        """
        logger.info(f"Shutting down {self.mod_name} adapter for agent {self.agent_id}")
        return True

    async def on_connect(self) -> None:
        """Called when the mod adapter is connected to the network.

        Announces the agent's capabilities when connecting to the network.
        """
        if self._capabilities:
            await self._announce_capabilities()
            logger.info(f"Agent {self.agent_id} connected and announced capabilities")

    async def set_capabilities(self, capabilities: Dict[str, Any]) -> None:
        """Set the capabilities for this agent.

        Args:
            capabilities: The capabilities to set
        """
        self._capabilities = capabilities
        logger.info(f"Agent {self.agent_id} set capabilities: {capabilities}")

        # If already connected, announce the updated capabilities
        if self.connector and self.connector.is_connected:
            await self._announce_capabilities()

    async def update_capabilities(self, capabilities: Dict[str, Any]) -> None:
        """Update the capabilities for this agent.

        Args:
            capabilities: The capabilities to update
        """
        # Update capabilities with deep merge for nested structures
        # Make a deep copy of the capabilities to avoid reference issues
        capabilities_copy = copy.deepcopy(capabilities)

        # Update the capabilities dictionary
        for key, value in capabilities_copy.items():
            self._capabilities[key] = value

        logger.info(f"Agent {self.agent_id} updated capabilities: {self._capabilities}")

        # If already connected, announce the updated capabilities
        if self.connector and self.connector.is_connected:
            await self._announce_capabilities()

    async def discover_agents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover agents with specific capabilities.

        Args:
            query: Query parameters for capability matching

        Returns:
            List[Dict[str, Any]]: List of matching agents with their capabilities
        """
        if not self.connector or not self.connector.is_connected:
            logger.warning(
                f"Agent {self.agent_id} cannot discover agents: not connected to network"
            )
            return []

        logger.info(f"Agent {self.agent_id} discovering agents with query: {query}")

        # Create discovery request message
        message = Event(
            event_name="discovery.request",
            source_id=self.agent_id,
            relevant_mod=self.mod_name,
            destination_id=self.agent_id,
            payload={"action": DISCOVER_AGENTS, "query": query},
        )

        # Send the message and wait for response
        await self.connector.send_mod_message(message)

        # Wait for the discovery_results response with a filter for the action
        response = await self.connector.wait_mod_message(
            self.mod_name, filter_dict={"action": "discovery_results"}
        )

        if response:
            results = response.content.get("results", [])
            logger.info(
                f"Agent {self.agent_id} received {len(results)} discovery results"
            )
            return results

        logger.warning(f"Agent {self.agent_id} received no discovery results")
        return []

    async def process_incoming_mod_message(self, message: Event) -> Optional[Event]:
        """Process an incoming protocol message.

        Args:
            message: The message to handle

        Returns:
            Optional[Event]: The processed message, or None for stopping the message from being processed further by other adapters
        """
        if message.mod != self.mod_name:
            return message

        # Handle discovery results
        if message.content.get("action") == "discovery_results":
            logger.info(
                f"Agent {self.agent_id} received discovery results: {len(message.content.get('results', []))} agents"
            )
            # The results will be handled by the discover_agents method
            return None

        return message

    async def _announce_capabilities(self) -> None:
        """Announce this agent's capabilities to the network."""
        if not self.connector or not self.agent_id:
            logger.warning("Cannot announce capabilities: not connected or no agent ID")
            return

        logger.info(
            f"Agent {self.agent_id} announcing capabilities: {self._capabilities}"
        )
        logger.debug(f"Capabilities type: {type(self._capabilities)}")
        if "language_models" in self._capabilities:
            logger.debug(
                f"Language models: {self._capabilities['language_models']}, type: {type(self._capabilities['language_models'])}"
            )

        # Make a deep copy of capabilities to avoid reference issues
        capabilities_copy = copy.deepcopy(self._capabilities)

        # Create announcement message with explicit direction=inbound
        message = Event(
            event_name="discovery.announce",
            source_id=self.agent_id,
            relevant_mod=self.mod_name,
            destination_id=self.agent_id,
            payload={
                "action": ANNOUNCE_CAPABILITIES,
                "capabilities": capabilities_copy,
            },
        )

        logger.debug(f"Sending capabilities message: {message.content}")

        # Send the message
        await self.connector.send_mod_message(message)

    def get_tools(self) -> List[AgentTool]:
        """Get the tools for the mod adapter.

        Returns:
            List[AgentAdapterTool]: The tools for the mod adapter
        """
        tools = []

        # Tool for discovering agents with specific capabilities
        discover_agents_tool = AgentTool(
            name="discover_agents",
            description="Discover agents with specific capabilities",
            input_schema={
                "type": "object",
                "properties": {
                    "capability_filter": {
                        "type": "object",
                        "description": "Filter criteria for agent capabilities",
                    }
                },
                "required": ["capability_filter"],
            },
            func=self.discover_agents,
        )
        tools.append(discover_agents_tool)

        # Tool for setting this agent's capabilities
        announce_capabilities_tool = AgentTool(
            name="announce_capabilities",
            description="Announce this agent's capabilities to the network",
            input_schema={
                "type": "object",
                "properties": {
                    "capabilities": {
                        "type": "object",
                        "description": "Capabilities to set for this agent",
                    }
                },
                "required": ["capabilities"],
            },
            func=self.set_capabilities,
        )
        tools.append(announce_capabilities_tool)

        return tools

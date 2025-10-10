"""
Agent network implementation for OpenAgents.

This module provides the network architecture using the transport and topology abstractions.
"""

import logging
import uuid
import time
import yaml
from typing import (
    Dict,
    Any,
    List,
    Optional,
    Callable,
    Awaitable,
    OrderedDict,
    Union,
    Set,
    TYPE_CHECKING,
)

from openagents.config.globals import (
    SYSTEM_AGENT_ID,
    SYSTEM_EVENT_REGISTER_AGENT,
    SYSTEM_EVENT_UNREGISTER_AGENT,
    SYSTEM_EVENT_POLL_MESSAGES,
    SYSTEM_NOTIFICAITON_REGISTER_AGENT,
    SYSTEM_NOTIFICAITON_UNREGISTER_AGENT,
    WORKSPACE_DEFAULT_MOD_NAME,
)
from openagents.core.base_mod import BaseMod
from openagents.models.event_response import EventResponse

if TYPE_CHECKING:
    from openagents.core.workspace import Workspace
from pathlib import Path

from openagents.models.transport import TransportType
from openagents.core.topology import NetworkMode, AgentConnection, create_topology
from openagents.models.messages import Event, EventNames
from openagents.models.network_config import (
    NetworkConfig,
    NetworkMode as ConfigNetworkMode,
)
from openagents.core.agent_identity import AgentIdentityManager
from openagents.models.event import Event, EventNames, EventVisibility
from openagents.core.event_gateway import EventGateway
from openagents.core.secret_manager import SecretManager

logger = logging.getLogger(__name__)


class AgentNetwork:
    """Agent network implementation using transport and topology abstractions."""

    def __init__(self, config: NetworkConfig, workspace_path: Optional[str]):
        """Initialize the agent network.

        Args:
            config: Network configuration
            workspace_path: Optional workspace directory path for persistent storage.
                            If None, a temporary workspace will be created.
        """
        self.config = config
        self.network_name = config.name
        self.network_id = config.node_id or f"network-{uuid.uuid4().hex[:8]}"

        # Workspace manager for persistent storage
        self.workspace_manager = None
        if workspace_path:
            from openagents.core.workspace_manager import WorkspaceManager

            self.workspace_manager = WorkspaceManager(workspace_path)
            self.workspace_manager.initialize_workspace()
        else:
            # Create temporal workspace when workspace_path is None
            from openagents.core.workspace_manager import create_temporary_workspace

            self.workspace_manager = create_temporary_workspace()

        # Create topology
        topology_mode = (
            NetworkMode.DECENTRALIZED
            if str(config.mode) == str(ConfigNetworkMode.DECENTRALIZED)
            else NetworkMode.CENTRALIZED
        )
        self.topology = create_topology(topology_mode, self.network_id, self.config)

        # Network state
        self.is_running = False
        self.start_time: Optional[float] = None

        # Connection management
        self.metadata: Dict[str, Any] = {}

        # Agent and mod tracking (for compatibility with system commands)
        self.mods: OrderedDict[str, BaseMod] = OrderedDict()
        self.mod_manifests: Dict[str, Any] = {}

        # Agent identity management
        self.identity_manager = AgentIdentityManager()


        self.secret_manager = SecretManager()

        # Event gateway
        self.event_gateway = EventGateway(self)

    @property
    def events(self) -> EventGateway:
        """Get the events interface for this network.

        Returns:
            EventGateway: The network's event gateway for subscribing to events

        Example:
            # Subscribe to events at network level
            subscription = network.events.subscribe("agent1", ["project.*", "channel.message.*"])
        """
        return self.event_gateway

    @staticmethod
    def create_from_config(
        config: NetworkConfig, port: int = None, workspace_path: Optional[str] = None
    ) -> "AgentNetwork":
        """Create an AgentNetwork from a NetworkConfig object.

        Args:
            config: NetworkConfig object containing network configuration
            port: Optional port to use for the network
            workspace_path: Optional workspace directory path for persistent storage
        Returns:
            AgentNetwork: Initialized network instance with mods loaded
        """
        # Switch the port if provided
        if port is not None:
            config.network.port = port

        # Create the network instance
        network = AgentNetwork(config, workspace_path)

        # Load network mods if specified in config
        if config.mods:
            logger.info(
                f"Loading {len(config.mods)} network mods from NetworkConfig..."
            )
            try:
                from openagents.utils.mod_loaders import load_network_mods

                # Convert ModConfig objects to dictionaries for load_network_mods
                mod_configs = []
                for mod_config in config.mods:
                    if hasattr(mod_config, "model_dump"):
                        # Pydantic model
                        mod_configs.append(mod_config.model_dump())
                    elif hasattr(mod_config, "dict"):
                        # Older Pydantic model
                        mod_configs.append(mod_config.dict())
                    else:
                        # Already a dictionary
                        mod_configs.append(mod_config)

                mods = load_network_mods(mod_configs)

                for mod_name, mod_instance in mods.items():
                    mod_instance.bind_network(network)
                    network.mods[mod_name] = mod_instance
                    logger.info(f"Registered network mod: {mod_name}")

                logger.info(f"Successfully loaded {len(mods)} network mods")

            except Exception as e:
                logger.warning(f"Failed to load network mods: {e}")

        return network

    @staticmethod
    def load(
        config: Union[str, Path, None] = None,
        port: int = None,
        workspace_path: Optional[str] = None,
    ) -> "AgentNetwork":
        """Load an AgentNetwork from a YAML configuration file.

        Args:
            config: String or Path to a YAML config file, or None to auto-discover in workspace_path
            port: Optional port to use for the network
            workspace_path: Optional workspace directory path for persistent storage
        Returns:
            AgentNetwork: Initialized network instance

        Raises:
            FileNotFoundError: If config file path doesn't exist
            ValueError: If config file is invalid or missing required fields, or if config is None and no network.yaml found
            TypeError: If config is not a string, Path, or None (NetworkConfig objects should use create_from_config())

        Examples:
            # Load from YAML file path
            network = AgentNetwork.load("examples/centralized_network_config.yaml")
            network = AgentNetwork.load(Path("config/network.yaml"))

            # Auto-discover network.yaml in workspace directory
            network = AgentNetwork.load(None, workspace_path="./my_workspace")

            # For NetworkConfig objects, use create_from_config() instead:
            network_config = NetworkConfig(name="MyNetwork", mode="centralized")
            network = AgentNetwork.create_from_config(network_config)
        """
        if isinstance(config, NetworkConfig) or (
            hasattr(config, "__class__")
            and config.__class__.__name__ == "NetworkConfig"
        ):
            raise TypeError(
                "NetworkConfig objects are not supported in load(). "
                "Use AgentNetwork.create_from_config(config) instead for NetworkConfig objects."
            )

        elif config is None:
            # Auto-discover network.yaml in workspace_path
            if not workspace_path:
                raise ValueError(
                    "workspace_path must be provided when config is None for auto-discovery"
                )

            workspace_dir = Path(workspace_path)
            config_path = workspace_dir / "network.yaml"

            if not config_path.exists():
                raise FileNotFoundError(
                    f"No network.yaml found in workspace directory: {workspace_path}"
                )

            logger.info(f"Auto-discovered network configuration: {config_path}")
            config = config_path  # Set config to the discovered path and continue with normal processing

        if isinstance(config, (str, Path)):
            # Load from YAML file path
            config_path = Path(config)

            if not config_path.exists():
                raise FileNotFoundError(
                    f"Network configuration file not found: {config_path}"
                )

            try:
                with open(config_path, "r") as f:
                    config_dict = yaml.safe_load(f)

                # Extract network configuration from YAML
                if "network" not in config_dict:
                    raise ValueError(
                        f"Configuration file {config_path} must contain a 'network' section"
                    )

                network_config = NetworkConfig(**config_dict["network"])
                logger.info(f"Loaded network configuration from {config_path}")

                # Create the network instance using create_from_config for consistent mod loading
                network = AgentNetwork.create_from_config(
                    network_config, port, workspace_path
                )

                # Load metadata if specified in config
                if "metadata" in config_dict:
                    network.metadata.update(config_dict["metadata"])
                    logger.debug(f"Loaded metadata: {config_dict['metadata']}")

                return network

            except yaml.YAMLError as e:
                raise ValueError(
                    f"Invalid YAML in configuration file {config_path}: {e}"
                )
            except Exception as e:
                raise ValueError(
                    f"Error loading network configuration from {config_path}: {e}"
                )

        else:
            raise TypeError(
                f"config must be NetworkConfig, str, Path, or None, got {type(config)}"
            )

    def _register_internal_handlers(self):
        """Register internal message handlers."""
        assert self.topology is not None
        self.topology.register_event_handler(self.process_external_event)

    async def _log_event(self, event: Event):
        """Global event handler for logging and routing."""
        logger.debug(
            f"Event: {event.event_name} from {event.source_id} to {event.destination_id or 'all'}"
        )

    async def emit_to_event_bus(self, event: Event) -> None:
        """
        Emit an event through the unified event system.

        Args:
            event: The event to emit
        """
        await self.event_bus.emit_event(event)

    async def initialize(self) -> bool:
        """Initialize the network.

        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize topology
            if not await self.topology.initialize():
                logger.error("Failed to initialize network topology")
                return False

            # Re-register message handlers after topology initialization
            self._register_internal_handlers()

            self.is_running = True
            self.start_time = time.time()

            logger.info(f"Agent network '{self.network_name}' initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agent network: {e}")
            return False

    async def shutdown(self) -> bool:
        """Shutdown the network.

        Returns:
            bool: True if shutdown successful
        """
        try:
            self.is_running = False

            # Shutdown topology
            await self.topology.shutdown()

            logger.info(f"Agent network '{self.network_name}' shutdown successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to shutdown agent network: {e}")
            return False

    async def register_agent(
        self,
        agent_id: str,
        transport_type: TransportType,
        metadata: Dict[str, Any],
        certificate: str,
        force_reconnect: bool = False,
        password_hash: Optional[str] = None,
    ) -> EventResponse:
        """Register an agent with the network.

        Args:
            agent_id: Unique identifier for the agent
            transport_type: Transport type used by the agent
            metadata: Agent metadata including capabilities
            certificate: Agent certificate
            force_reconnect: Whether to force reconnect
            password_hash: Password hash for group authentication (direct parameter, not in metadata)

        Returns:
            bool: True if registration successful
        """

        # Create agent info
        agent_info = AgentConnection(
            agent_id=agent_id,
            metadata=metadata,
            last_seen=time.time(),
            transport_type=transport_type,
        )

        # Register with topology
        if await self.topology.is_agent_registered(agent_id):
            can_override = False
            logger.info(f"Agent {agent_id} already registered with network")
            if certificate and self.identity_manager.validate_agent(
                agent_id, certificate
            ):
                can_override = True
            elif force_reconnect:
                can_override = True

            if can_override:
                await self.topology.unregister_agent(agent_id)
            else:
                return EventResponse(
                    success=False,
                    message=f"Agent {agent_id} already registered with network",
                )

        success = await self.topology.register_agent(agent_info, password_hash=password_hash)

        if success:
            # Generate and store authentication secret
            secret = self.secret_manager.generate_secret(agent_id)

            # Group assignment is now handled by topology layer

            # Register agent with event gateway to create event queue
            self.event_gateway.register_agent(agent_id)

            # Notify mods about agent registration
            registration_notification = Event(
                event_name=SYSTEM_NOTIFICAITON_REGISTER_AGENT,
                source_id=SYSTEM_AGENT_ID,
                payload={"agent_id": agent_id, "metadata": metadata},
            )
            await self.process_external_event(registration_notification)

            # Get assigned group from topology
            assigned_group = self.topology.agent_group_membership.get(agent_id, "default")
            logger.info(f"Registered agent {agent_id} with network in group '{assigned_group}'")

            return EventResponse(
                success=True,
                message=f"Registered agent {agent_id} with network",
                data={"secret": secret},
            )
        else:
            # Check if rejection was due to password requirement
            error_message = f"Failed to register agent {agent_id} with network"
            if self.config.requires_password:
                error_message = "Password authentication required for network registration"

            logger.error(f"Failed to register agent {agent_id} with network")
            return EventResponse(
                success=False,
                message=error_message,
            )

    async def unregister_agent(self, agent_id: str) -> EventResponse:
        """Unregister an agent from the network.

        Args:
            agent_id: ID of the agent to unregister

        Returns:
            bool: True if unregistration successful
        """
        success = await self.topology.unregister_agent(agent_id)

        if success:
            # Remove authentication secret
            self.secret_manager.remove_secret(agent_id)

            await self.event_gateway.cleanup_agent(agent_id)
            logger.info(f"Unregistered agent {agent_id} from network")
            await self.process_external_event(
                Event(
                    event_name=SYSTEM_NOTIFICAITON_UNREGISTER_AGENT,
                    source_id=SYSTEM_AGENT_ID,
                    payload={"agent_id": agent_id},
                )
            )
            return EventResponse(
                success=True, message=f"Unregistered agent {agent_id} from network"
            )
        else:
            return EventResponse(
                success=False,
                message=f"Failed to unregister agent {agent_id} from network",
            )

    def get_agent_registry(self) -> Dict[str, AgentConnection]:
        """Get all agents in the network.

        Returns:
            Dict[str, AgentInfo]: Dictionary of agent ID to agent info
        """
        return self.topology.get_agent_registry()

    def get_agent(self, agent_id: str) -> Optional[AgentConnection]:
        """Get information about a specific agent.

        Args:
            agent_id: ID of the agent

        Returns:
            Optional[AgentInfo]: Agent info if found, None otherwise
        """
        return self.topology.get_agent_connection(agent_id)

    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics.

        Returns:
            Dict[str, Any]: Network statistics including group information
        """
        uptime = time.time() - self.start_time if self.start_time else 0
        agent_registry = self.get_agent_registry()

        # Build groups dictionary: group_name -> list of agent_ids
        # Use topology's agent_group_membership
        groups: Dict[str, List[str]] = {}
        for agent_id, group_name in self.topology.agent_group_membership.items():
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(agent_id)

        # Build group config info (without tokens for security)
        group_config = []
        added_group_names = set()
        for group_name, group_cfg in self.config.agent_groups.items():
            added_group_names.add(group_name)
            group_config.append({
                "name": group_name,
                "description": group_cfg.description,
                "agent_count": len(groups.get(group_name, [])),
                "metadata": group_cfg.metadata,
            })

        # Add default group info if it has agents
        default_group_name = self.config.default_agent_group
        if default_group_name not in added_group_names:
            added_group_names.add(default_group_name)
            group_config.append({
                "name": default_group_name,
                "description": "Agents without valid credentials",
                "agent_count": len(groups.get(default_group_name, [])),
                "metadata": {},
            })

        return {
            "network_id": self.network_id,
            "network_name": self.network_name,
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "agent_count": len(agent_registry),
            "agents": {
                agent_id: {
                    "capabilities": info.capabilities,
                    "last_seen": info.last_seen,
                    "transport_type": info.transport_type,
                    "address": info.address,
                    "group": self.topology.agent_group_membership.get(agent_id, self.config.default_agent_group),
                }
                for agent_id, info in agent_registry.items()
            },
            "groups": groups,
            "group_config": group_config,
            "mods": [mod.model_dump() for mod in self.config.mods],
            "topology_mode": (
                self.config.mode
                if isinstance(self.config.mode, str)
                else self.config.mode.value
            ),
            "transports": [
                transport.model_dump() for transport in self.config.transports
            ],
            "manifest_transport": self.config.manifest_transport,
            "recommended_transport": self.config.recommended_transport,
            "max_connections": self.config.max_connections,
        }

    async def process_external_event(self, event: Event) -> EventResponse:
        """Handle incoming transport messages.

        Args:
            event: Transport event to handle
        """
        # Skip authentication for system events that don't have secrets
        # But authenticate system events that do include secrets (like authenticated polling/unregistration)
        # Special cases: polling and unregistration always require authentication
        is_system_event = event.source_id == SYSTEM_AGENT_ID or event.event_name.startswith("system.")
        has_secret = hasattr(event, "secret") and event.secret
        is_polling_event = event.event_name == SYSTEM_EVENT_POLL_MESSAGES
        is_unregister_event = event.event_name == SYSTEM_EVENT_UNREGISTER_AGENT
        
        if is_system_event and not has_secret and not is_polling_event and not is_unregister_event:
            # System events without secrets bypass authentication (registration, etc.)
            # But polling and unregistration always require authentication
            return await self.event_gateway.process_event(event)

        # Validate authentication secret for all other events (unless disabled for testing)
        if not self.config.disable_agent_secret_verification and not self._validate_event_authentication(
            event
        ):
            logger.warning(f"Authentication failed for event from {event.source_id}")
            return EventResponse(
                success=False,
                message="Authentication failed: Invalid or missing secret",
            )

        return await self.event_gateway.process_event(event)

    async def process_event(self, event: Event) -> EventResponse:
        """Handle internal events from mods that bypass authentication.
        
        This method should be used by mods when sending internal notifications
        or events that don't need authentication validation.
        
        Args:
            event: Internal event to handle
        """
        logger.debug(f"Processing internal event: {event.event_name} from {event.source_id}")
        return await self.event_gateway.process_event(event)

    def _validate_event_authentication(self, event: Event) -> bool:
        """Validate the authentication secret for an event.

        Args:
            event: The event to validate

        Returns:
            bool: True if authentication is valid, False otherwise
        """
        # Check if secret is provided
        if not hasattr(event, "secret") or not event.secret:
            return False

        # Validate the secret
        return self.secret_manager.validate_secret(event.source_id, event.secret)

    def workspace(self, client_id: Optional[str] = None) -> "Workspace":
        """Create a workspace instance for this network.

        This method creates a workspace that provides access to channels and collaboration
        features through the thread messaging mod. The workspace requires the
        openagents.mods.workspace.default mod to be enabled in the network.

        Args:
            client_id: Optional client ID for the workspace connection.
                      If not provided, a random ID will be generated.

        Returns:
            Workspace: A workspace instance for channel communication

        Raises:
            RuntimeError: If the workspace.default mod is not enabled in the network
        """
        # Check if workspace.default mod is enabled
        if WORKSPACE_DEFAULT_MOD_NAME not in self.mods:
            available_mods = list(self.mods.keys())
            raise RuntimeError(
                f"Workspace functionality requires the '{WORKSPACE_DEFAULT_MOD_NAME}' mod to be enabled in the network. "
                f"Available mods: {available_mods}. "
                f"Please add '{WORKSPACE_DEFAULT_MOD_NAME}' to your network configuration."
            )

        # Import here to avoid circular imports
        from openagents.core.client import AgentClient
        from openagents.core.workspace import Workspace

        # Create a client for the workspace
        if client_id is None:
            import uuid

            client_id = f"workspace-client-{uuid.uuid4().hex[:8]}"

        client = AgentClient(client_id)

        # Create workspace with network reference
        workspace = Workspace(client, network=self)

        # Automatically connect the workspace client to the network
        try:
            # Use the same host and port as the network
            host = self.config.host if self.config.host != "0.0.0.0" else "localhost"
            port = self.config.port

            logger.info(
                f"Auto-connecting workspace client {client_id} to {host}:{port}"
            )

            # Connect asynchronously - this needs to be awaited by the caller
            # We'll create a method that handles the connection
            workspace._auto_connect_config = {"host": host, "port": port}

        except Exception as e:
            logger.warning(
                f"Could not prepare auto-connection for workspace client: {e}"
            )

        logger.info(f"Created workspace with client ID: {client_id}")
        return workspace


def create_network(config: Union[NetworkConfig, str, Path]) -> AgentNetwork:
    """Create an agent network from configuration.

    Args:
        config: Network configuration (NetworkConfig object, file path string, or Path object)

    Returns:
        AgentNetwork: Configured network instance

    Examples:
        # From NetworkConfig object
        network = create_network(NetworkConfig(name="MyNetwork"))

        # From YAML file path
        network = create_network("examples/centralized_network_config.yaml")
        network = create_network(Path("config/network.yaml"))
    """
    if isinstance(config, NetworkConfig) or (
        hasattr(config, "__class__") and config.__class__.__name__ == "NetworkConfig"
    ):
        return AgentNetwork.create_from_config(config)
    else:
        return AgentNetwork.load(config)


# Backward compatibility aliases
AgentNetworkServer = AgentNetwork
EnhancedAgentNetwork = AgentNetwork  # For transition period
create_enhanced_network = create_network  # For transition period

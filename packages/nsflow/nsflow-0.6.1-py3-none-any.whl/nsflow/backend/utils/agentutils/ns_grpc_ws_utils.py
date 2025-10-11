
# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# nsflow SDK Software in commercial settings.
#
# END COPYRIGHT

import asyncio
import json
import os
import logging
import tempfile
from typing import Dict, Any
import uuid

from fastapi import WebSocket, WebSocketDisconnect

from neuro_san.client.agent_session_factory import AgentSessionFactory

from nsflow.backend.utils.agentutils.async_streaming_input_processor import AsyncStreamingInputProcessor

from nsflow.backend.utils.logutils.websocket_logs_registry import LogsRegistry
from nsflow.backend.utils.tools.ns_configs_registry import NsConfigsRegistry
from nsflow.backend.utils.agentutils.agent_log_processor import AgentLogProcessor

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize a lock
user_sessions_lock = asyncio.Lock()
user_sessions = {}

# Global storage for latest sly_data by network name
latest_sly_data_storage: Dict[str, Any] = {}


# pylint: disable=too-many-instance-attributes
class NsGrpcWsUtils:
    """
    Encapsulates gRPC session management and WebSocket interactions for a NeuroSAN agent.
    Manages:
    - WebSocket message handling
    - gRPC streaming communication
    - Live logging and internal chat broadcasting via WebSocketLogsManager
    """

    LOG_BUFFER_SIZE = 100
    DEFAULT_INPUT: str = ""
    DEFAULT_PROMPT: str = "Please enter your response ('quit' to terminate):\n"

    def __init__(self, agent_name: str,
                 websocket: WebSocket):
        """
        Initialize the gRPC service API wrapper.
        :param agent_name: Name of the NeuroSAN agent(Network) to connect to.
        :param websocket: The WebSocket connection instance.
        :param forwarded_request_metadata: List of metadata keys to extract from incoming headers.
        """
        try:
            config = NsConfigsRegistry.get_current()
        except RuntimeError as e:
            raise RuntimeError("No active NsConfigStore. \
                               Please set it via /set_config before using gRPC endpoints.") from e

        self.server_host = config.host
        self.server_port = config.port
        self.connection = config.connection_type

        self.agent_name = agent_name
        self.use_direct = False
        self.websocket = websocket
        self.active_chat_connections: Dict[str, WebSocket] = {}
        self.chat_context: Dict[str, Any] = {}
        # Set up the thinking file and directory from environment variables or defaults
        if "THINKING_FILE" not in os.environ:
            logging.warning("THINKING_FILE environment variable is not set. Using default temporary file.")
        self.thinking_file = os.getenv("THINKING_FILE", tempfile.gettempdir() + "/agent_thinking.txt")
        self.thinking_dir = os.getenv("THINKING_DIR", None)
        logging.info("Using thinking file: %s", self.thinking_file)
        logging.info("Using thinking dir: %s", self.thinking_dir)

        self.logs_manager = LogsRegistry.register(agent_name)
        self.session = self.create_agent_session()

    # pylint: disable=too-many-function-args
    async def handle_user_input(self):
        """
        Handle incoming WebSocket messages and process them using the gRPC session."""
        websocket = self.websocket
        await websocket.accept()
        sid = str(websocket.client) + "_" + str(uuid.uuid4().hex[:8])

        self.active_chat_connections[sid] = websocket
        await self.logs_manager.log_event(f"Chat client {sid} connected to agent: {self.agent_name}", "nsflow")

        async with user_sessions_lock:
            if sid not in user_sessions:
                user_sessions[sid] = await self.create_user_session(sid)
            user_session = user_sessions[sid]

        try:
            while True:
                websocket_data = await websocket.receive_text()
                message_data = json.loads(websocket_data)
                user_input = message_data.get("message", "")
                sly_data = message_data.get("sly_data", {})

                input_processor = user_session['input_processor']
                state = user_session['state']
                # Update user input in state
                state["user_input"] = user_input
                # Update sly_data in state based on user input
                state["sly_data"].update(sly_data)

                # Update the state
                state = await input_processor.async_process_once(state)
                user_session['state'] = state
                last_chat_response = state.get("last_chat_response")

                # Start a background task and pass necessary data
                if last_chat_response:
                    # try:
                    response_str = json.dumps({"message": {"type": "AI", "text": last_chat_response}})
                    sly_data_str = {"text": state["sly_data"]}
                    await websocket.send_text(response_str)
                    await self.logs_manager.log_event(f"Streaming response sent: {response_str}", "nsflow")
                    await self.logs_manager.sly_data_event(sly_data_str)

                # Store the latest sly_data for this network
                if state.get("sly_data") is not None:
                    latest_sly_data_storage[self.agent_name] = state["sly_data"]
                    logging.info("Updated latest sly_data for network %s", self.agent_name)

                await self.logs_manager.log_event(f"Streaming chat finished for client: {sid}", "nsflow")

        except WebSocketDisconnect:
            await self.logs_manager.log_event(f"WebSocket chat client disconnected: {sid}", "nsflow")
        except Exception as e:
            logging.error("Unexpected error in WebSocket handler for %s: %s", sid, e)
            await self.logs_manager.log_event(f"Error in session {sid}: {e}", "nsflow")
        finally:
            # clean up
            self.active_chat_connections.pop(sid, None)
            async with user_sessions_lock:
                user_sessions.pop(sid, None)

    async def create_user_session(self, sid: str) -> Dict[str, Any]:
        """method to create a user session with the given WebSocket connection."""

        # Agent session gets created in init
        chat_filter: Dict[str, Any] = {"chat_filter_type": "MAXIMAL"}
        state: Dict[str, Any] = {
            "last_chat_response": None,
            "num_input": 0,
            "chat_filter": chat_filter,
            "sly_data": {},
        }

        # agent_session = self.base_utils.get_regular_agent_grpc_session(metadata=metadata)
        input_processor = AsyncStreamingInputProcessor(default_input="",
                                                  thinking_file=self.thinking_file,
                                                  session=self.session,
                                                  thinking_dir=self.thinking_dir)
        # Add a processor to handle agent logs
        # and to highlight the agents that respond in the agent network diagram
        agent_log_processor = AgentLogProcessor(self.agent_name, sid)
        input_processor.processor.add_processor(agent_log_processor)

        # Note: If nothing is specified the server assumes the chat_filter_type
        #       should be "MINIMAL", however for this client which is aimed at
        #       developers, we specifically want a default MAXIMAL client to
        #       show all the bells and whistles of the output that a typical
        #       end user will not care about and not appreciate the extra
        #       data charges on their cell phone.

        user_session = {
            'input_processor': input_processor,
            'state': state
        }
        return user_session

    def create_agent_session(self):
        """Open a session with the factory"""
         # Open a session with the factory
        factory: AgentSessionFactory = self.get_agent_session_factory()
        metadata: Dict[str, str] = {"user_id": os.environ.get("USER")}
        session = factory.create_session(self.connection, self.agent_name,
                                              self.server_host, self.server_port, self.use_direct,
                                              metadata)
        return session

    def get_connectivity(self):
        """Simple method to get connectivity details"""
        data: Dict[str, Any] = {}
        return self.session.connectivity(data)

    def get_agent_session_factory(self) -> AgentSessionFactory:
        """
        This allows subclasses to add different kinds of connections.

        :return: An AgentSessionFactory instance that will allow creation of the
                 session with the agent network.
        """
        return AgentSessionFactory()

    @classmethod
    def get_latest_sly_data(cls, network_name: str) -> dict:
        """
        Retrieve the latest sly_data for a given network.
        
        Args:
            network_name: The name of the network to get sly_data for
            
        Returns:
            dict: The latest sly_data for the network, or empty dict if none available
        """
        return latest_sly_data_storage.get(network_name, {})

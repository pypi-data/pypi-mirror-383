"""ACP (Agent Client Protocol) session management for llmling-agent.

This module provides session lifecycle management, state tracking, and coordination
between agents and ACP clients through the JSON-RPC protocol.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

from pydantic_ai import Agent as PydanticAIAgent

from acp.schema import (
    AgentMessageChunk,
    AvailableCommandsUpdate,
    SessionNotification,
    TextContentBlock,
)
from llmling_agent.log import get_logger
from llmling_agent.mcp_server.manager import MCPManager
from llmling_agent_acp.acp_tools import ACPCapabilityResourceProvider
from llmling_agent_acp.command_bridge import is_slash_command
from llmling_agent_acp.converters import (
    convert_acp_mcp_server_to_config,
    create_thought_chunk,
    format_tool_call_for_acp,
    from_content_blocks,
    to_session_updates,
)


# Tools that send their own rich ACP notifications (with ToolCallLocation, etc.)
# These tools are excluded from generic session-level notifications to prevent duplication
ACP_SELF_NOTIFYING_TOOLS = {"read_text_file", "write_text_file", "run_command"}


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pydantic_ai import ModelRequestNode
    from pydantic_ai.agent import CallToolsNode
    from pydantic_ai.run import AgentRun

    from acp import Client
    from acp.acp_types import ContentBlock, MCPServer, StopReason
    from acp.schema import AvailableCommand, ClientCapabilities
    from llmling_agent import Agent, AgentPool
    from llmling_agent.models.content import BaseContent
    from llmling_agent_acp.acp_agent import LLMlingACPAgent
    from llmling_agent_acp.command_bridge import ACPCommandBridge

    # from llmling_agent_acp.permission_server import PermissionMCPServer
    from llmling_agent_providers.base import UsageLimits


logger = get_logger(__name__)


class ACPSession:
    """Individual ACP session state and management.

    Manages the lifecycle and state of a single ACP session, including:
    - Agent instance and conversation state
    - Working directory and environment
    - MCP server connections
    - File system bridge for client operations
    - Tool execution and streaming updates
    """

    def __init__(
        self,
        session_id: str,
        agent_pool: AgentPool[Any],
        current_agent_name: str,
        cwd: str,
        client: Client,
        mcp_servers: Sequence[MCPServer] | None = None,
        usage_limits: UsageLimits | None = None,
        command_bridge: ACPCommandBridge | None = None,
        acp_agent: LLMlingACPAgent | None = None,
        client_capabilities: ClientCapabilities | None = None,
    ) -> None:
        """Initialize ACP session.

        Args:
            session_id: Unique session identifier
            agent_pool: AgentPool containing available agents
            current_agent_name: Name of currently active agent
            cwd: Working directory for the session
            client: External library Client interface for operations
            mcp_servers: Optional MCP server configurations
            usage_limits: Optional usage limits for model requests and tokens
            command_bridge: Optional command bridge for slash commands
            acp_agent: ACP agent instance for capability tools
            client_capabilities: Client capabilities for tool registration
        """
        self.session_id = session_id
        self.agent_pool = agent_pool
        self.current_agent_name = current_agent_name
        self.cwd = cwd
        self.client = client
        self.mcp_servers = mcp_servers or []
        self.usage_limits = usage_limits

        # Session state
        self._active = True
        self._task_lock = asyncio.Lock()
        self._cancelled = False
        self.command_bridge = command_bridge
        self.mcp_manager: MCPManager | None = None
        # self.permission_server: PermissionMCPServer | None = None
        self.capability_provider: ACPCapabilityResourceProvider | None = None
        if acp_agent and client_capabilities:
            self.capability_provider = ACPCapabilityResourceProvider(
                agent=acp_agent,
                session_id=session_id,
                client_capabilities=client_capabilities,
                cwd=self.cwd,
            )
            # Add capability provider to current agent
            current_agent = self.agent_pool.get_agent(current_agent_name)
            current_agent.tools.add_provider(self.capability_provider)

        # Add cwd context to all agents in the pool
        for agent in self.agent_pool.agents.values():
            agent.sys_prompts.prompts.append(self.get_cwd_context)  # pyright: ignore[reportArgumentType]

        msg = "Created ACP session %s with agent pool (current: %s)"
        logger.info(msg, session_id, current_agent_name)

    async def initialize_mcp_servers(self) -> None:
        """Initialize MCP servers if any are configured."""
        # Always initialize permission server first
        # await self._initialize_permission_server()

        if not self.mcp_servers:
            return

        msg = "Initializing %d MCP servers for session %s"
        logger.info(msg, len(self.mcp_servers), self.session_id)
        cfgs = [convert_acp_mcp_server_to_config(s) for s in self.mcp_servers]
        # Initialize MCP manager with converted configs
        name = f"session_{self.session_id}"

        # Create progress handler for MCP to ACP bridging
        from llmling_agent_acp.mcp_progress import create_acp_progress_handler

        progress_handler = create_acp_progress_handler(self)

        # Define accessible roots for MCP servers
        accessible_roots = []
        if self.cwd:
            accessible_roots.append(str(self.cwd))

        self.mcp_manager = MCPManager(
            name,
            servers=cfgs,
            context=self.agent.context,
            progress_handler=progress_handler,
            accessible_roots=accessible_roots,
        )
        try:
            # Start MCP manager and, fetch and add tools
            await self.mcp_manager.__aenter__()
            mcp_tools = await self.mcp_manager.get_tools()
            for tool in mcp_tools:
                self.agent.tools.register_tool(tool)
            msg = "Added %d MCP tools to current agent for session %s"
            logger.info(msg, len(mcp_tools), self.session_id)

            # Log the tool schemas for debugging
            for tool in mcp_tools:
                msg = "Registered MCP tool %s with schema: %s"
                logger.debug(msg, tool.name, tool.schema)

            # Register MCP prompts as slash commands
            await self._register_mcp_prompts_as_commands()

        except Exception:
            msg = "Failed to initialize MCP manager for session %s"
            logger.exception(msg, self.session_id)
            # Don't fail session creation, just log the error
            self.mcp_manager = None

    # async def _initialize_permission_server(self) -> None:
    #     """Initialize the permission MCP server for this session."""
    #     try:
    #         from acp.schema import HttpMcpServer
    #         from llmling_agent_acp.permission_server import PermissionMCPServer

    #         # Create permission server
    #         self.permission_server = PermissionMCPServer(
    #             client=self.client, session_id=self.session_id
    #         )

    #         # Start HTTP server
    #         url, port = await self.permission_server.start()
    #         logger.info(
    #             "Permission server started for session %s at %s:%d",
    #             self.session_id,
    #             url,
    #             port,
    #         )

    #         # Add permission server to MCP servers list
    #         permission_mcp = HttpMcpServer(
    #             name="acp-permission",
    #             url=f"{url}/mcp",
    #             headers=[HttpHeader(name="x-acp-session-id", value=self.session_id)],
    #         )

    #         # Add to session's MCP servers (create list if None)
    #         if self.mcp_servers is None:
    #             self.mcp_servers = []

    #         # Convert to list if it's not already (in case it's a tuple/sequence)
    #         if not isinstance(self.mcp_servers, list):
    #             self.mcp_servers = list(self.mcp_servers)

    #         self.mcp_servers.append(permission_mcp)

    #     except Exception:
    #         logger.exception(
    #             "Failed to initialize permission server for session %s", self.session_id
    #         )
    #         # Don't fail session creation, just log the error
    #         self.permission_server = None

    @property
    def agent(self) -> Agent[Any]:
        """Get the currently active agent."""
        return self.agent_pool.get_agent(self.current_agent_name)

    def get_cwd_context(self) -> str:
        """Get current working directory context for prompts."""
        return f"Working directory: {self.cwd}" if self.cwd else ""

    async def switch_active_agent(self, agent_name: str) -> None:
        """Switch to a different agent in the pool.

        Args:
            agent_name: Name of the agent to switch to

        Raises:
            ValueError: If agent not found in pool
        """
        if agent_name not in self.agent_pool.agents:
            available = list(self.agent_pool.agents.keys())
            msg = f"Agent '{agent_name}' not found. Available: {available}"
            raise ValueError(msg)

        old_agent_name = self.current_agent_name
        self.current_agent_name = agent_name

        # Move capability provider from old agent to new agent
        if self.capability_provider:
            old_agent = self.agent_pool.get_agent(old_agent_name)
            new_agent = self.agent_pool.get_agent(agent_name)

            old_agent.tools.remove_provider(self.capability_provider)
            new_agent.tools.add_provider(self.capability_provider)

        msg = "Session %s switched from agent %s to %s"
        logger.info(msg, self.session_id, old_agent_name, agent_name)
        # Update available commands since different agents may have different tools
        await self.send_available_commands_update()

    @property
    def active(self) -> bool:
        """Check if session is active."""
        return self._active

    def cancel(self) -> None:
        """Cancel the current prompt turn."""
        self._cancelled = True
        logger.info("Session %s cancelled", self.session_id)

    def is_cancelled(self) -> bool:
        """Check if the session is cancelled."""
        return self._cancelled

    async def process_prompt(
        self, content_blocks: Sequence[ContentBlock]
    ) -> AsyncGenerator[SessionNotification | StopReason]:
        """Process a prompt request and stream responses.

        Args:
            content_blocks: List of content blocks from the prompt request

        Yields:
            SessionNotification objects for streaming to client, or StopReason literal
        """
        if not self._active:
            msg = "Attempted to process prompt on inactive session %s"
            logger.warning(msg, self.session_id)
            yield "refusal"
            return

        # Reset cancellation flag
        self._cancelled = False

        async with self._task_lock:
            try:
                # Check for cancellation
                if self._cancelled:
                    yield "cancelled"
                    return

                # Convert content blocks to structured content
                contents = from_content_blocks(content_blocks)
                logger.info("Converted content: %r", contents)

                if not contents:
                    msg = "Empty prompt received for session %s"
                    logger.warning(msg, self.session_id)
                    yield "refusal"
                    return

                # Check for slash commands in text content
                commands = []
                non_command_content = []

                for item in contents:
                    if isinstance(item, str) and is_slash_command(item):
                        # Found a slash command
                        command_text = item.strip()
                        logger.info("Found slash command: %s", command_text)
                        commands.append(command_text)
                    else:
                        non_command_content.append(item)

                # Process commands if found
                if commands and self.command_bridge:
                    for command in commands:
                        logger.info("Processing slash command: %s", command)
                        async for (
                            notification
                        ) in self.command_bridge.execute_slash_command(command, self):
                            yield notification

                    # If only commands, end turn
                    if not non_command_content:
                        yield "end_turn"
                        return

                # Pass structured content to agent for processing
                msg = "Processing prompt for session %s with %d content items"
                logger.debug(msg, self.session_id, len(non_command_content))
                notification_count = 0
                stop_reason = None
                async for result in self._process_iter_response(non_command_content):
                    if isinstance(result, str):
                        # Stop reason received
                        stop_reason = result
                        break
                    # Session notification
                    notification_count += 1
                    msg = "Yielding notification %d for session %s"
                    logger.info(msg, notification_count, self.session_id)
                    yield result

                # Yield the final stop reason
                final_stop_reason = stop_reason or "end_turn"
                msg = "Finished streaming, sent %d notifications, stop reason: %s"
                logger.info(msg, notification_count, final_stop_reason)
                yield final_stop_reason

            except Exception as e:
                logger.exception("Error processing prompt in session %s", self.session_id)
                # Send error as agent message
                msg = f"I encountered an error while processing your request: {e}"
                error_updates = to_session_updates(msg, self.session_id)
                for error_update in error_updates:
                    yield error_update
                # Return refusal for errors
                yield "refusal"

    async def _process_iter_response(  # noqa: PLR0915
        self, content: list[str | BaseContent]
    ) -> AsyncGenerator[SessionNotification | StopReason]:
        """Process content using agent iteration for comprehensive streaming.

        Args:
            content: List of content objects (strings and Content objects)

        Yields:
            SessionNotification objects for all agent execution events,
            or StopReason literal
        """
        from pydantic_ai.exceptions import UsageLimitExceeded

        msg = "Starting agent.iterate_run for session %s with %d content items"
        logger.info(msg, self.session_id, len(content))
        logger.info("Agent model: %s", self.agent.model_name)

        try:
            async with self.agent.iterate_run(
                *content, usage_limits=self.usage_limits
            ) as agent_run:
                logger.info("Agent run started for session %s", self.session_id)
                node_count = 0
                has_yielded_anything = False
                async for node in agent_run:
                    if self._cancelled:
                        yield "cancelled"
                        return

                    node_count += 1
                    msg = "Processing node %d (%s) for session %s"
                    logger.info(msg, node_count, type(node).__name__, self.session_id)
                    if PydanticAIAgent.is_user_prompt_node(node):
                        # User prompt node - log but don't stream (already processed)
                        msg = "Processing user prompt node for session %s"
                        logger.debug(msg, self.session_id)

                    elif PydanticAIAgent.is_model_request_node(node):
                        # Model request node - stream the model's response
                        msg = "Starting model request streaming for session %s"
                        logger.info(msg, self.session_id)
                        notification_count = 0
                        async for result in self._stream_model_request(node, agent_run):
                            if isinstance(result, str):
                                # Stop reason from model request
                                yield result
                                return
                            elif result:
                                notification_count += 1
                                has_yielded_anything = True
                                msg = "Yielding model notification %d for session %s"
                                logger.info(msg, notification_count, self.session_id)
                                yield result
                        msg = "Model request streaming finished, yielded %d notifications"
                        logger.info(msg, notification_count)

                    elif PydanticAIAgent.is_call_tools_node(node):
                        # Tool execution node - stream tool calls and results
                        msg = "Starting tool execution streaming for session %s"
                        logger.info(msg, self.session_id)
                        async for notification in self._stream_tool_execution(
                            node, agent_run
                        ):
                            if notification:
                                has_yielded_anything = True
                                yield notification

                    elif (
                        PydanticAIAgent.is_end_node(node)
                        and agent_run.result
                        and agent_run.result.output
                    ):
                        final_content = str(agent_run.result.output)
                        msg = "End node reached with output: %r"
                        logger.info(msg, final_content[:100])
                        if final_content.strip():
                            # Send final response as session update if nothing streamed
                            if not has_yielded_anything:
                                msg = (
                                    "No streaming occurred,"
                                    "sending final response for session %s"
                                )
                                logger.info(msg, self.session_id)
                                content_block = TextContentBlock(text=final_content)
                                update = AgentMessageChunk(content=content_block)
                                notification = SessionNotification(
                                    session_id=self.session_id, update=update
                                )
                                has_yielded_anything = True
                                yield notification
                            msg = "Agent iteration completed for session %s"
                            logger.debug(msg, self.session_id)
                    else:
                        msg = "Unknown node type for session %s: %s"
                        logger.info(msg, self.session_id, type(node).__name__)

                msg = "Agent iteration finished. Processed %d nodes, yielded anything: %s"
                logger.info(msg, node_count, has_yielded_anything)

        except UsageLimitExceeded as e:
            logger.info("Usage limit exceeded for session %s: %s", self.session_id, e)
            # Determine which limit was exceeded based on the error message
            error_msg = str(e)

            # Check for request limit (maps to max_turn_requests)
            if "request_limit" in error_msg:
                yield "max_turn_requests"
            # Check for any token limits (maps to max_tokens)
            elif any(limit in error_msg for limit in ["tokens_limit", "token_limit"]):
                yield "max_tokens"
            # Tool call limits don't have a direct ACP stop reason, treat as refusal
            elif "tool_calls_limit" in error_msg or "tool call" in error_msg:
                yield "refusal"
            else:
                # Default to max_tokens for other usage limits
                yield "max_tokens"
        except Exception as e:
            logger.exception("Error in agent iteration for session %s", self.session_id)
            logger.info("Sending error updates for session %s", self.session_id)
            error_updates = to_session_updates(f"Agent error: {e}", self.session_id)
            for error_update in error_updates:
                yield error_update

    async def _stream_model_request(
        self,
        node: ModelRequestNode[Any, Any],
        agent_run: AgentRun[Any, Any],
    ) -> AsyncGenerator[SessionNotification | StopReason]:
        """Stream model request events.

        Args:
            node: Model request node
            agent_run: Agent run context

        Yields:
            SessionNotification objects for model streaming, or StopReason literal
        """
        from pydantic_ai.messages import (
            FinalResultEvent,
            PartDeltaEvent,
            PartStartEvent,
            TextPartDelta,
            ThinkingPartDelta,
            ToolCallPartDelta,
        )

        try:
            async with node.stream(agent_run.ctx) as request_stream:
                event_count = 0
                msg = "Starting to iterate over request_stream events for session %s"
                logger.info(msg, self.session_id)
                async for event in request_stream:
                    # Check for cancellation
                    if self._cancelled:
                        yield "cancelled"
                        return

                    event_count += 1
                    msg = "Received event %d: %s for session %s"
                    logger.info(msg, event_count, type(event).__name__, self.session_id)
                    match event:
                        case PartStartEvent():
                            # Part started - could log but don't stream yet
                            pass

                        case PartDeltaEvent(
                            delta=TextPartDelta(content_delta=content)
                        ) if content:
                            msg = "Processing TextPartDelta (length=%d) %r for session %s"
                            logger.info(msg, len(content), content[:100], self.session_id)
                            # Stream text deltas directly as single agent message chunks
                            content_block = TextContentBlock(text=content)
                            update = AgentMessageChunk(content=content_block)
                            notification = SessionNotification(
                                session_id=self.session_id, update=update
                            )
                            msg = "Yielding TextPartDelta notification for session %s"
                            logger.info(msg, self.session_id)
                            yield notification

                        case PartDeltaEvent(delta=TextPartDelta(content_delta=content)):
                            msg = "Received empty/falsy TextPartDelta %r for session %s"
                            logger.info(msg, content, self.session_id)

                        case PartDeltaEvent(
                            delta=ThinkingPartDelta(content_delta=content)
                        ) if content:
                            msg = "Processing ThinkingPartDelta %r for session %s"
                            logger.info(msg, content, self.session_id)
                            thought_notification = create_thought_chunk(
                                content, self.session_id
                            )
                            yield thought_notification

                        case PartDeltaEvent(delta=ToolCallPartDelta()):
                            msg = "Received ToolCallPartDelta for session %s"
                            logger.info(msg, self.session_id)
                        case FinalResultEvent():
                            msg = "Received FinalResultEvent for session %s"
                            logger.info(msg, self.session_id)
                            break

                        case _:
                            msg = "Received unhandled event type: %s for session %s"
                            logger.info(msg, type(event).__name__, self.session_id)

        except Exception:
            msg = "Error streaming model request for session %s"
            logger.exception(msg, self.session_id)
            yield "refusal"

    async def _stream_tool_execution(
        self,
        node: CallToolsNode[Any, Any],
        agent_run: AgentRun[Any, Any],
    ) -> AsyncGenerator[SessionNotification]:
        """Stream tool execution events.

        Args:
            node: Tool execution node
            agent_run: Agent run context

        Yields:
            SessionNotification objects for tool execution
        """
        from pydantic_ai.messages import (
            FunctionToolCallEvent,
            FunctionToolResultEvent,
            RetryPromptPart,
            ToolReturnPart,
        )

        # Track tool call inputs by tool_call_id
        inputs: dict[str, dict] = {}

        try:
            async with node.stream(agent_run.ctx) as tool_stream:
                async for event in tool_stream:
                    match event:
                        case FunctionToolCallEvent() as tool_event:
                            # Tool call started - save input for later use
                            tool_call_id = tool_event.part.tool_call_id
                            inputs[tool_call_id] = tool_event.part.args_as_dict()

                            # Skip generic notifications for self-notifying tools
                            if tool_event.part.tool_name not in ACP_SELF_NOTIFYING_TOOLS:
                                tool_notification = format_tool_call_for_acp(
                                    tool_name=tool_event.part.tool_name,
                                    tool_input=tool_event.part.args_as_dict(),
                                    tool_output=None,  # Not available yet
                                    session_id=self.session_id,
                                    status="pending",
                                    tool_call_id=tool_call_id,
                                )
                                yield tool_notification

                        case FunctionToolResultEvent() as result_event if isinstance(
                            result_event.result, ToolReturnPart
                        ):
                            # Tool call completed successfully
                            tool_call_id = result_event.tool_call_id
                            tool_input = inputs.get(tool_call_id, {})

                            # Check if the tool result is a streaming AsyncGenerator
                            if isinstance(result_event.result.content, AsyncGenerator):
                                # Stream the tool output chunks
                                full_content = ""
                                async for chunk in result_event.result.content:
                                    full_content += str(chunk)

                                    # Yield intermediate streaming notification
                                    # Skip generic notifications for self-notifying tools
                                    if (
                                        result_event.result.tool_name
                                        not in ACP_SELF_NOTIFYING_TOOLS
                                    ):
                                        streaming_notification = format_tool_call_for_acp(
                                            tool_name=result_event.result.tool_name,
                                            tool_input=tool_input,
                                            tool_output=chunk,
                                            session_id=self.session_id,
                                            status="in_progress",
                                            tool_call_id=tool_call_id,
                                        )
                                        yield streaming_notification

                                # Replace the AsyncGenerator with the full content to
                                # prevent errors
                                result_event.result.content = full_content
                                final_output = full_content
                            else:
                                final_output = result_event.result.content

                            # Final completion notification
                            # Skip generic notifications for self-notifying tools
                            if (
                                result_event.result.tool_name
                                not in ACP_SELF_NOTIFYING_TOOLS
                            ):
                                tool_notification = format_tool_call_for_acp(
                                    tool_name=result_event.result.tool_name,
                                    tool_input=tool_input,
                                    tool_output=final_output,
                                    session_id=self.session_id,
                                    status="completed",
                                    tool_call_id=tool_call_id,
                                )
                                yield tool_notification

                            # Clean up stored input
                            inputs.pop(tool_call_id, None)

                        case FunctionToolResultEvent() as result_event if isinstance(
                            result_event.result, RetryPromptPart
                        ):
                            # Tool call failed and needs retry
                            tool_call_id = result_event.tool_call_id
                            tool_input = inputs.get(tool_call_id, {})
                            tool_name = result_event.result.tool_name or "unknown"
                            error_message = result_event.result.model_response()

                            # Skip generic notifications for self-notifying tools
                            if tool_name not in ACP_SELF_NOTIFYING_TOOLS:
                                tool_notification = format_tool_call_for_acp(
                                    tool_name=tool_name,
                                    tool_input=tool_input,
                                    tool_output=f"Error: {error_message}",
                                    session_id=self.session_id,
                                    status="failed",
                                    tool_call_id=tool_call_id,
                                )
                                yield tool_notification
                            # Clean up stored input
                            inputs.pop(tool_call_id, None)

        except Exception:
            msg = "Error streaming tool execution for session %s"
            logger.exception(msg, self.session_id)

    async def execute_tool(
        self, tool_name: str, tool_params: dict[str, Any]
    ) -> AsyncGenerator[SessionNotification]:
        """Execute a tool and stream the results.

        Args:
            tool_name: Name of the tool to execute
            tool_params: Parameters to pass to the tool

        Yields:
            SessionNotification objects for tool execution updates
        """
        try:
            try:
                tool = self.agent.tools[tool_name]
            except KeyError:
                msg = "Tool %s not found in agent %s"
                logger.warning(msg, tool_name, self.agent.name)
                return
            result = await tool.execute(**tool_params)

            # Format as ACP tool call notification
            notification = format_tool_call_for_acp(
                tool_name=tool_name,
                tool_input=tool_params,
                tool_output=result,
                session_id=self.session_id,
                status="completed",
            )

            yield notification

        except Exception as e:
            msg = "Error executing tool %s in session %s"
            logger.exception(msg, tool_name, self.session_id)
            error_notification = format_tool_call_for_acp(
                tool_name=tool_name,
                tool_input=tool_params,
                tool_output=f"Error: {e}",
                session_id=self.session_id,
                status="failed",
            )

            yield error_notification

    async def close(self) -> None:
        """Close the session and cleanup resources."""
        if not self._active:
            return

        self._active = False

        try:
            # Clean up permission server if present
            # if self.permission_server:
            #     await self.permission_server.stop()
            #     self.permission_server = None

            # Clean up MCP manager if present
            if self.mcp_manager:
                await self.mcp_manager.cleanup()
                self.mcp_manager = None

            # Clean up capability provider if present
            if self.capability_provider:
                current_agent = self.agent_pool.get_agent(self.current_agent_name)
                current_agent.tools.remove_provider(self.capability_provider)

            # Remove cwd context callable from all agents
            for agent in self.agent_pool.agents.values():
                if self.get_cwd_context in agent.sys_prompts.prompts:
                    agent.sys_prompts.prompts.remove(self.get_cwd_context)  # pyright: ignore[reportArgumentType]
                self.capability_provider = None

            # Note: Individual agents are managed by the pool's lifecycle
            # The pool will handle agent cleanup when it's closed
            logger.info("Closed ACP session %s", self.session_id)
        except Exception:
            logger.exception("Error closing session %s", self.session_id)

    async def send_available_commands_update(self) -> None:
        """Send current available commands to client."""
        if not self.command_bridge:
            return

        try:
            commands = self.command_bridge.to_available_commands(self.agent.context)
            update = AvailableCommandsUpdate(available_commands=commands)
            notification = SessionNotification(session_id=self.session_id, update=update)
            await self.client.session_update(notification)

        except Exception:
            msg = "Failed to send available commands update for session %s"
            logger.exception(msg, self.session_id)

    async def update_available_commands(self, commands: list[AvailableCommand]) -> None:
        """Update and broadcast new command list.

        Args:
            commands: New list of available commands
        """
        try:
            update = AvailableCommandsUpdate(available_commands=commands)
            notification = SessionNotification(session_id=self.session_id, update=update)
            await self.client.session_update(notification)
            logger.debug("Updated available commands for session %s", self.session_id)
        except Exception:
            msg = "Failed to update available commands for session %s"
            logger.exception(msg, self.session_id)

    async def _register_mcp_prompts_as_commands(self) -> None:
        """Register MCP prompts as slash commands."""
        if not self.mcp_manager or not self.command_bridge:
            return

        try:
            # Collect all prompts from all MCP clients
            all_prompts = []
            for client in self.mcp_manager.clients.values():
                try:
                    result = await client.list_prompts()
                    all_prompts.extend(result.prompts)
                except Exception as e:  # noqa: BLE001
                    logger.warning("Failed to list prompts from MCP client: %s", e)

            # Register prompts as commands
            if all_prompts:
                self.command_bridge.add_mcp_prompt_commands(all_prompts)
                msg = "Registered %d MCP prompts as slash commands for session %s"
                logger.info(msg, len(all_prompts), self.session_id)

                # Send updated command list to client
                await self.send_available_commands_update()

        except Exception:
            msg = "Failed to register MCP prompts as commands for session %s"
            logger.exception(msg, self.session_id)

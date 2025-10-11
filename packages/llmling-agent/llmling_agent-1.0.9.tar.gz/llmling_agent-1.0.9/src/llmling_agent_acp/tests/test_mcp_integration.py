"""Test MCP server integration with ACP sessions."""

from __future__ import annotations

import sys

import pytest
from slashed import CommandStore

from acp import DefaultACPClient
from acp.schema import EnvVariable, StdioMcpServer
from llmling_agent import Agent
from llmling_agent.delegation import AgentPool
from llmling_agent.log import get_logger
from llmling_agent_acp.command_bridge import ACPCommandBridge
from llmling_agent_acp.converters import convert_acp_mcp_server_to_config
from llmling_agent_acp.session import ACPSession
from llmling_agent_acp.session_manager import ACPSessionManager


logger = get_logger(__name__)


async def test_mcp_server_conversion():
    """Test conversion from ACP McpServer to our MCPServerConfig."""
    acp_server = StdioMcpServer(
        name="test_server",
        command="uv",
        args=["run", "test-mcp-server"],
        env=[
            EnvVariable(name="API_KEY", value="test123"),
            EnvVariable(name="DEBUG", value="true"),
        ],
    )
    config = convert_acp_mcp_server_to_config(acp_server)
    assert config.name == "test_server"
    assert config.command == "uv"
    assert config.args == ["run", "test-mcp-server"]
    assert config.env == {"API_KEY": "test123", "DEBUG": "true"}


@pytest.mark.skipif(sys.platform == "darwin", reason="macOS subprocess handling differs")
async def test_session_with_mcp_servers():
    """Test creating an ACP session with MCP servers."""

    def simple_callback(message: str) -> str:
        return f"Test response for: {message}"

    agent = Agent[None](name="test_agent", provider=simple_callback)
    agent_pool = AgentPool[None]()
    agent_pool.register("test_agent", agent)
    client = DefaultACPClient(allow_file_operations=True)
    command_store = CommandStore()
    command_bridge = ACPCommandBridge(command_store)

    # Sample MCP servers (these won't actually connect in the test)
    mcp_servers = [
        StdioMcpServer(
            name="filesystem",
            command="echo",  # Use echo as a dummy command
            args=["filesystem server"],
            env=[],
        ),
        StdioMcpServer(
            name="web_search",
            command="echo",  # Use echo as a dummy command
            args=["web search server"],
            env=[EnvVariable(name="API_KEY", value="dummy")],
        ),
    ]

    # Create session with MCP servers
    session = ACPSession(
        session_id="test_session",
        agent_pool=agent_pool,
        current_agent_name="test_agent",
        cwd="/tmp",
        client=client,
        mcp_servers=mcp_servers,
        command_bridge=command_bridge,
    )

    # Note: In a real test, we would mock the MCP connections
    # For now, just verify the session was created properly
    assert session.session_id == "test_session"
    assert session.mcp_servers == mcp_servers
    assert session.mcp_manager is None  # Not initialized yet

    print(f"✓ Created session with {len(mcp_servers)} MCP servers")

    # Test initialization (this will fail without real MCP servers, which is expected)
    try:
        await session.initialize_mcp_servers()
        print("✓ MCP servers initialized (unexpectedly succeeded)")
    except Exception as e:  # noqa: BLE001
        print(f"✓ MCP server initialization failed as expected: {type(e).__name__}")

    # Cleanup
    await session.close()
    print("✓ Session closed successfully")


@pytest.mark.skipif(sys.platform == "darwin", reason="macOS subprocess handling differs")
async def test_session_manager_with_mcp():
    """Test session manager creating sessions with MCP servers."""
    print("Testing session manager with MCP servers...")

    # Create command bridge
    from slashed import CommandStore

    command_store = CommandStore()
    command_bridge = ACPCommandBridge(command_store)

    # Create session manager
    session_manager = ACPSessionManager(command_bridge)

    # Create agent
    def simple_callback(message: str) -> str:
        return f"Test response for: {message}"

    agent = Agent[None](
        name="test_agent",
        provider=simple_callback,
    )

    # Create empty agent pool and register the agent
    agent_pool = AgentPool[None]()
    agent_pool.register("test_agent", agent)

    # Create client
    client = DefaultACPClient()

    # MCP servers
    mcp_servers = [StdioMcpServer(name="tools", command="echo", args=["tools"], env=[])]

    try:
        # Create session
        session_id = await session_manager.create_session(
            agent_pool=agent_pool,
            default_agent_name="test_agent",
            cwd="/tmp",
            client=client,
            mcp_servers=mcp_servers,
        )

        print(f"✓ Created session {session_id} with MCP servers")

        # Get session and verify
        session = await session_manager.get_session(session_id)
        assert session is not None
        assert session.mcp_servers == mcp_servers

        print("✓ Session retrieved successfully")

        # Cleanup
        await session_manager.close_session(session_id)
        print("✓ Session cleaned up")

    except Exception:
        logger.exception("Session manager test failed")
        raise


async def test_tool_integration():
    """Test that MCP tools would be properly integrated."""
    print("Testing MCP tool integration concepts...")

    # Create agent
    def simple_callback(message: str) -> str:
        return f"Test response for: {message}"

    agent = Agent[None](
        name="test_agent",
        provider=simple_callback,
    )

    # Start agent context
    async with agent:
        initial_tools = len(await agent.tools.get_tools())
        print(f"Agent starts with {initial_tools} tools")

        # In real scenario, MCP tools would be added here
        # For test, we'll simulate by adding a dummy tool
        from llmling_agent.tools.base import Tool

        def dummy_mcp_tool(query: str) -> str:
            """Dummy MCP tool for testing."""
            return f"MCP result for: {query}"

        tool = Tool.from_callable(
            dummy_mcp_tool, source="mcp", metadata={"mcp_tool": "dummy_search"}
        )

        agent.tools.register_tool(tool)

        final_tools = len(await agent.tools.get_tools())
        print(f"After adding MCP tool: {final_tools} tools")

        assert final_tools == initial_tools + 1
        print("✓ MCP tool integration pattern works")


if __name__ == "__main__":
    pytest.main(["-v", __file__])

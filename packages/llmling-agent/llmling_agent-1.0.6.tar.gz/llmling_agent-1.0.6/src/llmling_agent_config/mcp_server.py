"""MCP server configuration."""

from __future__ import annotations

import os
from typing import Annotated, Literal

from pydantic import ConfigDict, Field
from schemez import Schema


TransportType = Literal["stdio", "sse", "streamable-http"]


class MCPServerAuthSettings(Schema):
    """Represents authentication configuration for a server.

    Minimal OAuth v2.1 support with sensible defaults.
    """

    oauth: bool = False

    # Local callback server configuration
    redirect_port: int = 3030
    redirect_path: str = "/callback"

    # Optional scope override. If set to a list, values are space-joined.
    scope: str | list[str] | None = None

    # Token persistence: use OS keychain via 'keyring' by default; fallback to 'memory'.
    persist: Literal["keyring", "memory"] = "keyring"


class BaseMCPServerConfig(Schema):
    """Base model for MCP server configuration."""

    type: str
    """Type discriminator for MCP server configurations."""

    name: str | None = None
    """Optional name for referencing the server."""

    enabled: bool = True
    """Whether this server is currently enabled."""

    env: dict[str, str] | None = None
    """Environment variables to pass to the server process."""

    timeout: float = 30.0
    """Timeout for the server process."""

    def get_env_vars(self) -> dict[str, str]:
        """Get environment variables for the server process."""
        env = os.environ.copy()
        if self.env:
            env.update(self.env)
        env["PYTHONIOENCODING"] = "utf-8"
        return env


class StdioMCPServerConfig(BaseMCPServerConfig):
    """MCP server started via stdio.

    Uses subprocess communication through standard input/output streams.
    """

    type: Literal["stdio"] = Field("stdio", init=False)
    """Stdio server coniguration."""

    command: str
    """Command to execute (e.g. "pipx", "python", "node")."""

    args: list[str] = Field(default_factory=list)
    """Command arguments (e.g. ["run", "some-server", "--debug"])."""

    @classmethod
    def from_string(cls, command: str) -> StdioMCPServerConfig:
        """Create a MCP server from a command string."""
        cmd, args = command.split(maxsplit=1)
        return cls(command=cmd, args=args.split())


class SSEMCPServerConfig(BaseMCPServerConfig):
    """MCP server using Server-Sent Events transport.

    Connects to a server over HTTP with SSE for real-time communication.
    """

    type: Literal["sse"] = Field("sse", init=False)
    """SSE server configuration."""

    url: str
    """URL of the SSE server endpoint."""

    auth: MCPServerAuthSettings = Field(default_factory=MCPServerAuthSettings)
    """OAuth settings for the SSE server."""


class StreamableHTTPMCPServerConfig(BaseMCPServerConfig):
    """MCP server using StreamableHttp.

    Connects to a server over HTTP with streamable HTTP.
    """

    type: Literal["streamable-http"] = Field("streamable-http", init=False)
    """HTTP server configuration."""

    url: str
    """URL of the HTTP server endpoint."""

    auth: MCPServerAuthSettings = Field(default_factory=MCPServerAuthSettings)
    """OAuth settings for the HTTP server."""


MCPServerConfig = Annotated[
    StdioMCPServerConfig | SSEMCPServerConfig | StreamableHTTPMCPServerConfig,
    Field(discriminator="type"),
]


class PoolServerConfig(Schema):
    """Configuration for pool-based MCP server."""

    enabled: bool = False
    """Whether this server is currently enabled."""

    # Resource exposure control
    serve_nodes: list[str] | bool = True
    """Which nodes to expose as tools:
    - True: All nodes
    - False: No nodes
    - list[str]: Specific node names
    """

    serve_prompts: list[str] | bool = True
    """Which prompts to expose:
    - True: All prompts from manifest
    - False: No prompts
    - list[str]: Specific prompt names
    """

    # Transport configuration
    transport: TransportType = "stdio"
    """Transport type to use."""

    host: str = "localhost"
    """Host to bind server to (SSE / Streamable-HTTP only)."""

    port: int = 3001
    """Port to listen on (SSE / Streamable-HTTP only)."""

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    """Allowed CORS origins (SSE / Streamable-HTTP only)."""

    zed_mode: bool = False
    """Enable Zed editor compatibility mode."""

    model_config = ConfigDict(frozen=True)

    def should_serve_node(self, name: str) -> bool:
        """Check if a node should be exposed."""
        match self.serve_nodes:
            case True:
                return True
            case False:
                return False
            case list():
                return name in self.serve_nodes
            case _:
                return False

    def should_serve_prompt(self, name: str) -> bool:
        """Check if a prompt should be exposed."""
        match self.serve_prompts:
            case True:
                return True
            case False:
                return False
            case list():
                return name in self.serve_prompts
            case _:
                return False

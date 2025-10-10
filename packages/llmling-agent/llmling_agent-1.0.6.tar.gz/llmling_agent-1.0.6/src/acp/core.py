"""Client ACP Connection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from acp.meta import AgentMethod, ClientMethod

from acp.agent.protocol import Agent
from acp.client.protocol import Client
from acp.connection import Connection
from acp.exceptions import RequestError
from acp.schema import (
    AuthenticateRequest,
    AuthenticateResponse,
    CancelNotification,
    CreateTerminalRequest,
    CreateTerminalResponse,
    InitializeRequest,
    InitializeResponse,
    KillTerminalCommandRequest,
    KillTerminalCommandResponse,
    LoadSessionRequest,
    LoadSessionResponse,
    ModelInfo,
    NewSessionRequest,
    NewSessionResponse,
    PromptRequest,
    PromptResponse,
    ReadTextFileRequest,
    ReadTextFileResponse,
    ReleaseTerminalRequest,
    ReleaseTerminalResponse,
    RequestPermissionRequest,
    RequestPermissionResponse,
    SessionModelState,
    SessionNotification,
    SetSessionModelRequest,
    SetSessionModelResponse,
    SetSessionModeRequest,
    SetSessionModeResponse,
    TerminalOutputRequest,
    TerminalOutputResponse,
    WaitForTerminalExitRequest,
    WaitForTerminalExitResponse,
    WriteTextFileRequest,
    WriteTextFileResponse,
)


if TYPE_CHECKING:
    import asyncio
    from collections.abc import Callable, Sequence

    from tokonomics.model_discovery.model_info import ModelInfo as TokoModelInfo

    from acp.acp_types import MethodHandler


class AgentSideConnection(Client):
    """Agent-side connection.

    Use when you implement the Agent and need to talk to a Client.

    Args:
        to_agent: factory that receives this connection and returns your Agent
        input: asyncio.StreamWriter (local -> peer)
        output: asyncio.StreamReader (peer -> local)
    """

    def __init__(
        self,
        to_agent: Callable[[AgentSideConnection], Agent],
        input_stream: asyncio.StreamWriter,
        output_stream: asyncio.StreamReader,
        debug_messages: bool = False,
        debug_file: str | None = None,
    ) -> None:
        agent = to_agent(self)
        handler = _create_agent_handler(agent)
        self._conn = Connection(
            handler, input_stream, output_stream, debug_messages, debug_file
        )

    # client-bound methods (agent -> client)
    async def session_update(self, params: SessionNotification) -> None:
        dct = params.model_dump(by_alias=True, exclude_none=True)
        await self._conn.send_notification("session/update", dct)

    async def request_permission(
        self, params: RequestPermissionRequest
    ) -> RequestPermissionResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        method = "session/request_permission"
        resp = await self._conn.send_request(method, dct)
        return RequestPermissionResponse.model_validate(resp)

    async def read_text_file(self, params: ReadTextFileRequest) -> ReadTextFileResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("fs/read_text_file", dct)
        return ReadTextFileResponse.model_validate(resp)

    async def write_text_file(
        self, params: WriteTextFileRequest
    ) -> WriteTextFileResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        r = await self._conn.send_request("fs/write_text_file", dct)
        return WriteTextFileResponse.model_validate(r)

    # async def createTerminal(self, params: CreateTerminalRequest) -> TerminalHandle:
    async def create_terminal(
        self, params: CreateTerminalRequest
    ) -> CreateTerminalResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("terminal/create", dct)
        #  resp = CreateTerminalResponse.model_validate(resp)
        #  return TerminalHandle(resp.terminal_id, params.session_id, self._conn)
        return CreateTerminalResponse.model_validate(resp)

    async def ext_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        return await self._conn.send_request(f"_{method}", params)

    async def ext_notification(self, method: str, params: dict[str, Any]) -> None:
        await self._conn.send_notification(f"_{method}", params)

    async def terminal_output(
        self, params: TerminalOutputRequest
    ) -> TerminalOutputResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("terminal/output", dct)
        return TerminalOutputResponse.model_validate(resp)

    async def release_terminal(
        self, params: ReleaseTerminalRequest
    ) -> ReleaseTerminalResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("terminal/release", dct)
        return ReleaseTerminalResponse.model_validate(resp)

    async def wait_for_terminal_exit(
        self, params: WaitForTerminalExitRequest
    ) -> WaitForTerminalExitResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("terminal/wait_for_exit", dct)
        return WaitForTerminalExitResponse.model_validate(resp)

    async def kill_terminal(
        self, params: KillTerminalCommandRequest
    ) -> KillTerminalCommandResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("terminal/kill", dct)
        return KillTerminalCommandResponse.model_validate(resp)


class ClientSideConnection(Agent):
    """Client-side connection.

    Use when you implement the Client and need to talk to an Agent.

    Args:
      to_client: factory that receives this connection and returns your Client
      input: asyncio.StreamWriter (local -> peer)
      output: asyncio.StreamReader (peer -> local)
    """

    def __init__(
        self,
        to_client: Callable[[Agent], Client],
        input_stream: asyncio.StreamWriter,
        output_stream: asyncio.StreamReader,
    ) -> None:
        # Build client first so handler can delegate
        client = to_client(self)
        handler = self._create_handler(client)
        self._conn = Connection(handler, input_stream, output_stream)

    def _create_handler(self, client: Client) -> MethodHandler:
        """Create the method handler for client-side connection."""

        async def handler(
            method: ClientMethod | str,
            params: dict[str, Any] | None,
            is_notification: bool,
        ) -> (
            WriteTextFileResponse
            | ReadTextFileResponse
            | RequestPermissionResponse
            | SessionNotification
            | CreateTerminalResponse
            | TerminalOutputResponse
            | WaitForTerminalExitResponse
            | ReleaseTerminalResponse
            | KillTerminalCommandResponse
            | dict[str, Any]
            | None
        ):
            return await _handle_client_method(client, method, params, is_notification)

        return handler

    # agent-bound methods (client -> agent)
    async def initialize(self, params: InitializeRequest) -> InitializeResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("initialize", dct)
        return InitializeResponse.model_validate(resp)

    async def new_session(self, params: NewSessionRequest) -> NewSessionResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("session/new", dct)
        return NewSessionResponse.model_validate(resp)

    async def load_session(self, params: LoadSessionRequest) -> LoadSessionResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("session/load", dct)
        payload = resp if isinstance(resp, dict) else {}
        return LoadSessionResponse.model_validate(payload)

    async def set_session_mode(
        self, params: SetSessionModeRequest
    ) -> SetSessionModeResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("session/set_mode", dct)
        payload = resp if isinstance(resp, dict) else {}
        return SetSessionModeResponse.model_validate(payload)

    async def set_session_model(
        self, params: SetSessionModelRequest
    ) -> SetSessionModelResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("session/set_model", dct)
        payload = resp if isinstance(resp, dict) else {}
        return SetSessionModelResponse.model_validate(payload)

    async def authenticate(self, params: AuthenticateRequest) -> AuthenticateResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("authenticate", dct)
        payload = resp if isinstance(resp, dict) else {}
        return AuthenticateResponse.model_validate(payload)

    async def prompt(self, params: PromptRequest) -> PromptResponse:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        resp = await self._conn.send_request("session/prompt", dct)
        return PromptResponse.model_validate(resp)

    async def cancel(self, params: CancelNotification) -> None:
        dct = params.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        await self._conn.send_notification("session/cancel", dct)

    async def ext_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        return await self._conn.send_request(f"_{method}", params)

    async def ext_notification(self, method: str, params: dict[str, Any]) -> None:
        await self._conn.send_notification(f"_{method}", params)


async def _handle_client_method(  # noqa: PLR0911
    client: Client,
    method: ClientMethod | str,
    params: dict[str, Any] | None,
    is_notification: bool,
) -> (
    WriteTextFileResponse
    | ReadTextFileResponse
    | RequestPermissionResponse
    | SessionNotification
    | CreateTerminalResponse
    | TerminalOutputResponse
    | WaitForTerminalExitResponse
    | ReleaseTerminalResponse
    | KillTerminalCommandResponse
    | dict[str, Any]
    | None
):
    """Handle client method calls."""
    match method:
        case "fs/write_text_file":
            write_file_request = WriteTextFileRequest.model_validate(params)
            return await client.write_text_file(write_file_request)
        case "fs/read_text_file":
            read_file_request = ReadTextFileRequest.model_validate(params)
            return await client.read_text_file(read_file_request)
        case "session/request_permission":
            permission_request = RequestPermissionRequest.model_validate(params)
            return await client.request_permission(permission_request)
        case "session/update":
            notification = SessionNotification.model_validate(params)
            await client.session_update(notification)
            return None
        case "terminal/create":
            create_request = CreateTerminalRequest.model_validate(params)
            return await client.create_terminal(create_request)
        case "terminal/output":
            output_request = TerminalOutputRequest.model_validate(params)
            return await client.terminal_output(output_request)
        case "terminal/release":
            release_request = ReleaseTerminalRequest.model_validate(params)
            return await client.release_terminal(release_request)
        case "terminal/wait_for_exit":
            wait_request = WaitForTerminalExitRequest.model_validate(params)
            return await client.wait_for_terminal_exit(wait_request)
        case "terminal/kill":
            kill_request = KillTerminalCommandRequest.model_validate(params)
            return await client.kill_terminal(kill_request)
        case _ if method.startswith("_"):
            ext_name = method[1:]
            if is_notification:
                await client.ext_notification(ext_name, params or {})
                return None
            return await client.ext_method(ext_name, params or {})
        case _:
            raise RequestError.method_not_found(method)


# agent


async def _handle_agent_method(  # noqa: PLR0911
    agent: Agent,
    method: AgentMethod | str,
    params: dict[str, Any] | None,
    is_notification: bool,
) -> NewSessionResponse | InitializeResponse | PromptResponse | dict[str, Any] | None:
    match method:
        case "initialize":
            initialize_request = InitializeRequest.model_validate(params)
            return await agent.initialize(initialize_request)
        case "session/new":
            new_session_request = NewSessionRequest.model_validate(params)
            return await agent.new_session(new_session_request)
        case "session/load":
            load_request = LoadSessionRequest.model_validate(params)
            await agent.load_session(load_request)
            return None
        case "session/set_mode":
            set_mode_request = SetSessionModeRequest.model_validate(params)
            return (
                session_resp.model_dump(by_alias=True, exclude_none=True)
                if (session_resp := await agent.set_session_mode(set_mode_request))
                else {}
            )
        case "session/prompt":
            prompt_request = PromptRequest.model_validate(params)
            return await agent.prompt(prompt_request)
        case "session/cancel":
            cancel_notification = CancelNotification.model_validate(params)
            await agent.cancel(cancel_notification)
            return None
        case "session/set_model":
            set_model_request = SetSessionModelRequest.model_validate(params)
            return (
                model_result.model_dump(by_alias=True, exclude_none=True)
                if (model_result := await agent.set_session_model(set_model_request))
                else {}
            )
        case "authenticate":
            p = AuthenticateRequest.model_validate(params)
            result = await agent.authenticate(p)
            return result.model_dump(by_alias=True, exclude_none=True) if result else {}
        case _ if method.startswith("_"):
            ext_name = method[1:]
            if is_notification:
                await agent.ext_notification(ext_name, params or {})
                return None
            return await agent.ext_method(ext_name, params or {})
        case _:
            raise RequestError.method_not_found(method)


def _create_agent_handler(agent: Agent) -> MethodHandler:
    async def handler(
        method: AgentMethod | str,
        params: dict[str, Any] | None,
        is_notification: bool,
    ) -> Any:
        return await _handle_agent_method(agent, method, params, is_notification)

    return handler


def create_session_model_state(
    available_models: Sequence[TokoModelInfo], current_model: str | None = None
) -> SessionModelState | None:
    """Create a SessionModelState from available models.

    Args:
        available_models: List of all models the agent can switch between
        current_model: The currently active model (defaults to first available)

    Returns:
        SessionModelState with all available models, None if no models provided
    """
    if not available_models:
        return None
    # Create ModelInfo objects for each available model
    models = [
        ModelInfo(
            model_id=model.pydantic_ai_id,
            name=f"{model.provider}: {model.name}",
            description=model.description,
        )
        for model in available_models
    ]
    # Use first model as current if not specified
    all_ids = [model.pydantic_ai_id for model in available_models]
    current_model_id = current_model if current_model in all_ids else all_ids[0]
    return SessionModelState(available_models=models, current_model_id=current_model_id)

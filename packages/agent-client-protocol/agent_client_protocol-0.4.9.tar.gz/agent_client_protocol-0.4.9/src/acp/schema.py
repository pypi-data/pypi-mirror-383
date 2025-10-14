# Generated from schema/schema.json. Do not edit by hand.
# Schema ref: refs/tags/v0.4.9

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field, RootModel


PermissionOptionKind = Literal["allow_once", "allow_always", "reject_once", "reject_always"]
PlanEntryPriority = Literal["high", "medium", "low"]
PlanEntryStatus = Literal["pending", "in_progress", "completed"]
StopReason = Literal["end_turn", "max_tokens", "max_turn_requests", "refusal", "cancelled"]
ToolCallStatus = Literal["pending", "in_progress", "completed", "failed"]
ToolKind = Literal["read", "edit", "delete", "move", "search", "execute", "think", "fetch", "switch_mode", "other"]


class AuthenticateRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The ID of the authentication method to use.
    # Must be one of the methods advertised in the initialize response.
    methodId: Annotated[
        str,
        Field(
            description="The ID of the authentication method to use.\nMust be one of the methods advertised in the initialize response."
        ),
    ]


class AuthenticateResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None


class CommandInputHint(BaseModel):
    # A hint to display when the input hasn't been provided yet
    hint: Annotated[
        str,
        Field(description="A hint to display when the input hasn't been provided yet"),
    ]


class AvailableCommandInput(RootModel[CommandInputHint]):
    # The input specification for a command.
    root: Annotated[
        CommandInputHint,
        Field(description="The input specification for a command."),
    ]


class BlobResourceContents(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    blob: str
    mimeType: Optional[str] = None
    uri: str


class CreateTerminalResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The unique identifier for the created terminal.
    terminalId: Annotated[str, Field(description="The unique identifier for the created terminal.")]


class EnvVariable(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The name of the environment variable.
    name: Annotated[str, Field(description="The name of the environment variable.")]
    # The value to set for the environment variable.
    value: Annotated[str, Field(description="The value to set for the environment variable.")]


class FileSystemCapability(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Whether the Client supports `fs/read_text_file` requests.
    readTextFile: Annotated[
        Optional[bool],
        Field(description="Whether the Client supports `fs/read_text_file` requests."),
    ] = False
    # Whether the Client supports `fs/write_text_file` requests.
    writeTextFile: Annotated[
        Optional[bool],
        Field(description="Whether the Client supports `fs/write_text_file` requests."),
    ] = False


class HttpHeader(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The name of the HTTP header.
    name: Annotated[str, Field(description="The name of the HTTP header.")]
    # The value to set for the HTTP header.
    value: Annotated[str, Field(description="The value to set for the HTTP header.")]


class KillTerminalCommandResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None


class McpCapabilities(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Agent supports [`McpServer::Http`].
    http: Annotated[Optional[bool], Field(description="Agent supports [`McpServer::Http`].")] = False
    # Agent supports [`McpServer::Sse`].
    sse: Annotated[Optional[bool], Field(description="Agent supports [`McpServer::Sse`].")] = False


class HttpMcpServer(BaseModel):
    # HTTP headers to set when making requests to the MCP server.
    headers: Annotated[
        List[HttpHeader],
        Field(description="HTTP headers to set when making requests to the MCP server."),
    ]
    # Human-readable name identifying this MCP server.
    name: Annotated[str, Field(description="Human-readable name identifying this MCP server.")]
    type: Literal["http"]
    # URL to the MCP server.
    url: Annotated[str, Field(description="URL to the MCP server.")]


class SseMcpServer(BaseModel):
    # HTTP headers to set when making requests to the MCP server.
    headers: Annotated[
        List[HttpHeader],
        Field(description="HTTP headers to set when making requests to the MCP server."),
    ]
    # Human-readable name identifying this MCP server.
    name: Annotated[str, Field(description="Human-readable name identifying this MCP server.")]
    type: Literal["sse"]
    # URL to the MCP server.
    url: Annotated[str, Field(description="URL to the MCP server.")]


class StdioMcpServer(BaseModel):
    # Command-line arguments to pass to the MCP server.
    args: Annotated[
        List[str],
        Field(description="Command-line arguments to pass to the MCP server."),
    ]
    # Path to the MCP server executable.
    command: Annotated[str, Field(description="Path to the MCP server executable.")]
    # Environment variables to set when launching the MCP server.
    env: Annotated[
        List[EnvVariable],
        Field(description="Environment variables to set when launching the MCP server."),
    ]
    # Human-readable name identifying this MCP server.
    name: Annotated[str, Field(description="Human-readable name identifying this MCP server.")]


class ModelInfo(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Optional description of the model.
    description: Annotated[Optional[str], Field(description="Optional description of the model.")] = None
    # Unique identifier for the model.
    modelId: Annotated[str, Field(description="Unique identifier for the model.")]
    # Human-readable name of the model.
    name: Annotated[str, Field(description="Human-readable name of the model.")]


class NewSessionRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The working directory for this session. Must be an absolute path.
    cwd: Annotated[
        str,
        Field(description="The working directory for this session. Must be an absolute path."),
    ]
    # List of MCP (Model Context Protocol) servers the agent should connect to.
    mcpServers: Annotated[
        List[Union[HttpMcpServer, SseMcpServer, StdioMcpServer]],
        Field(description="List of MCP (Model Context Protocol) servers the agent should connect to."),
    ]


class PromptCapabilities(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Agent supports [`ContentBlock::Audio`].
    audio: Annotated[Optional[bool], Field(description="Agent supports [`ContentBlock::Audio`].")] = False
    # Agent supports embedded context in `session/prompt` requests.
    #
    # When enabled, the Client is allowed to include [`ContentBlock::Resource`]
    # in prompt requests for pieces of context that are referenced in the message.
    embeddedContext: Annotated[
        Optional[bool],
        Field(
            description="Agent supports embedded context in `session/prompt` requests.\n\nWhen enabled, the Client is allowed to include [`ContentBlock::Resource`]\nin prompt requests for pieces of context that are referenced in the message."
        ),
    ] = False
    # Agent supports [`ContentBlock::Image`].
    image: Annotated[Optional[bool], Field(description="Agent supports [`ContentBlock::Image`].")] = False


class ReadTextFileResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    content: str


class ReleaseTerminalResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None


class DeniedOutcome(BaseModel):
    outcome: Literal["cancelled"]


class AllowedOutcome(BaseModel):
    # The ID of the option the user selected.
    optionId: Annotated[str, Field(description="The ID of the option the user selected.")]
    outcome: Literal["selected"]


class RequestPermissionResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The user's decision on the permission request.
    outcome: Annotated[
        Union[DeniedOutcome, AllowedOutcome],
        Field(description="The user's decision on the permission request."),
    ]


class Role(Enum):
    assistant = "assistant"
    user = "user"


class SessionModelState(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The set of models that the Agent can use
    availableModels: Annotated[List[ModelInfo], Field(description="The set of models that the Agent can use")]
    # The current model the Agent is in.
    currentModelId: Annotated[str, Field(description="The current model the Agent is in.")]


class CurrentModeUpdate(BaseModel):
    # Unique identifier for a Session Mode.
    currentModeId: Annotated[str, Field(description="Unique identifier for a Session Mode.")]
    sessionUpdate: Literal["current_mode_update"]


class SetSessionModeRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The ID of the mode to set.
    modeId: Annotated[str, Field(description="The ID of the mode to set.")]
    # The ID of the session to set the mode for.
    sessionId: Annotated[str, Field(description="The ID of the session to set the mode for.")]


class SetSessionModeResponse(BaseModel):
    meta: Optional[Any] = None


class SetSessionModelRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The ID of the model to set.
    modelId: Annotated[str, Field(description="The ID of the model to set.")]
    # The ID of the session to set the model for.
    sessionId: Annotated[str, Field(description="The ID of the session to set the model for.")]


class SetSessionModelResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None


class TerminalExitStatus(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The process exit code (may be null if terminated by signal).
    exitCode: Annotated[
        Optional[int],
        Field(
            description="The process exit code (may be null if terminated by signal).",
            ge=0,
        ),
    ] = None
    # The signal that terminated the process (may be null if exited normally).
    signal: Annotated[
        Optional[str],
        Field(description="The signal that terminated the process (may be null if exited normally)."),
    ] = None


class TerminalOutputRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The session ID for this request.
    sessionId: Annotated[str, Field(description="The session ID for this request.")]
    # The ID of the terminal to get output from.
    terminalId: Annotated[str, Field(description="The ID of the terminal to get output from.")]


class TerminalOutputResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Exit status if the command has completed.
    exitStatus: Annotated[
        Optional[TerminalExitStatus],
        Field(description="Exit status if the command has completed."),
    ] = None
    # The terminal output captured so far.
    output: Annotated[str, Field(description="The terminal output captured so far.")]
    # Whether the output was truncated due to byte limits.
    truncated: Annotated[bool, Field(description="Whether the output was truncated due to byte limits.")]


class TextResourceContents(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    mimeType: Optional[str] = None
    text: str
    uri: str


class FileEditToolCallContent(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The new content after modification.
    newText: Annotated[str, Field(description="The new content after modification.")]
    # The original content (None for new files).
    oldText: Annotated[Optional[str], Field(description="The original content (None for new files).")] = None
    # The file path being modified.
    path: Annotated[str, Field(description="The file path being modified.")]
    type: Literal["diff"]


class TerminalToolCallContent(BaseModel):
    terminalId: str
    type: Literal["terminal"]


class ToolCallLocation(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Optional line number within the file.
    line: Annotated[Optional[int], Field(description="Optional line number within the file.", ge=0)] = None
    # The file path being accessed or modified.
    path: Annotated[str, Field(description="The file path being accessed or modified.")]


class WaitForTerminalExitRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The session ID for this request.
    sessionId: Annotated[str, Field(description="The session ID for this request.")]
    # The ID of the terminal to wait for.
    terminalId: Annotated[str, Field(description="The ID of the terminal to wait for.")]


class WaitForTerminalExitResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The process exit code (may be null if terminated by signal).
    exitCode: Annotated[
        Optional[int],
        Field(
            description="The process exit code (may be null if terminated by signal).",
            ge=0,
        ),
    ] = None
    # The signal that terminated the process (may be null if exited normally).
    signal: Annotated[
        Optional[str],
        Field(description="The signal that terminated the process (may be null if exited normally)."),
    ] = None


class WriteTextFileRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The text content to write to the file.
    content: Annotated[str, Field(description="The text content to write to the file.")]
    # Absolute path to the file to write.
    path: Annotated[str, Field(description="Absolute path to the file to write.")]
    # The session ID for this request.
    sessionId: Annotated[str, Field(description="The session ID for this request.")]


class WriteTextFileResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None


class AgentCapabilities(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Whether the agent supports `session/load`.
    loadSession: Annotated[Optional[bool], Field(description="Whether the agent supports `session/load`.")] = False
    # MCP capabilities supported by the agent.
    mcpCapabilities: Annotated[
        Optional[McpCapabilities],
        Field(description="MCP capabilities supported by the agent."),
    ] = McpCapabilities(http=False, sse=False)
    # Prompt capabilities supported by the agent.
    promptCapabilities: Annotated[
        Optional[PromptCapabilities],
        Field(description="Prompt capabilities supported by the agent."),
    ] = PromptCapabilities(audio=False, embeddedContext=False, image=False)


class Annotations(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    audience: Optional[List[Role]] = None
    lastModified: Optional[str] = None
    priority: Optional[float] = None


class AudioContent(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    data: str
    mimeType: str


class AuthMethod(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Optional description providing more details about this authentication method.
    description: Annotated[
        Optional[str],
        Field(description="Optional description providing more details about this authentication method."),
    ] = None
    # Unique identifier for this authentication method.
    id: Annotated[str, Field(description="Unique identifier for this authentication method.")]
    # Human-readable name of the authentication method.
    name: Annotated[str, Field(description="Human-readable name of the authentication method.")]


class AvailableCommand(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Human-readable description of what the command does.
    description: Annotated[str, Field(description="Human-readable description of what the command does.")]
    # Input for the command if required
    input: Annotated[
        Optional[AvailableCommandInput],
        Field(description="Input for the command if required"),
    ] = None
    # Command name (e.g., `create_plan`, `research_codebase`).
    name: Annotated[
        str,
        Field(description="Command name (e.g., `create_plan`, `research_codebase`)."),
    ]


class CancelNotification(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The ID of the session to cancel operations for.
    sessionId: Annotated[str, Field(description="The ID of the session to cancel operations for.")]


class ClientCapabilities(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # File system capabilities supported by the client.
    # Determines which file operations the agent can request.
    fs: Annotated[
        Optional[FileSystemCapability],
        Field(
            description="File system capabilities supported by the client.\nDetermines which file operations the agent can request."
        ),
    ] = FileSystemCapability(readTextFile=False, writeTextFile=False)
    # Whether the Client support all `terminal/*` methods.
    terminal: Annotated[
        Optional[bool],
        Field(description="Whether the Client support all `terminal/*` methods."),
    ] = False


class TextContentBlock(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    text: str
    type: Literal["text"]


class ImageContentBlock(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    data: str
    mimeType: str
    type: Literal["image"]
    uri: Optional[str] = None


class AudioContentBlock(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    data: str
    mimeType: str
    type: Literal["audio"]


class ResourceContentBlock(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    description: Optional[str] = None
    mimeType: Optional[str] = None
    name: str
    size: Optional[int] = None
    title: Optional[str] = None
    type: Literal["resource_link"]
    uri: str


class CreateTerminalRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Array of command arguments.
    args: Annotated[Optional[List[str]], Field(description="Array of command arguments.")] = None
    # The command to execute.
    command: Annotated[str, Field(description="The command to execute.")]
    # Working directory for the command (absolute path).
    cwd: Annotated[
        Optional[str],
        Field(description="Working directory for the command (absolute path)."),
    ] = None
    # Environment variables for the command.
    env: Annotated[
        Optional[List[EnvVariable]],
        Field(description="Environment variables for the command."),
    ] = None
    # Maximum number of output bytes to retain.
    #
    # When the limit is exceeded, the Client truncates from the beginning of the output
    # to stay within the limit.
    #
    # The Client MUST ensure truncation happens at a character boundary to maintain valid
    # string output, even if this means the retained output is slightly less than the
    # specified limit.
    outputByteLimit: Annotated[
        Optional[int],
        Field(
            description="Maximum number of output bytes to retain.\n\nWhen the limit is exceeded, the Client truncates from the beginning of the output\nto stay within the limit.\n\nThe Client MUST ensure truncation happens at a character boundary to maintain valid\nstring output, even if this means the retained output is slightly less than the\nspecified limit.",
            ge=0,
        ),
    ] = None
    # The session ID for this request.
    sessionId: Annotated[str, Field(description="The session ID for this request.")]


class ImageContent(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    data: str
    mimeType: str
    uri: Optional[str] = None


class InitializeRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Capabilities supported by the client.
    clientCapabilities: Annotated[
        Optional[ClientCapabilities],
        Field(description="Capabilities supported by the client."),
    ] = ClientCapabilities(fs=FileSystemCapability(readTextFile=False, writeTextFile=False), terminal=False)
    # The latest protocol version supported by the client.
    protocolVersion: Annotated[
        int,
        Field(
            description="The latest protocol version supported by the client.",
            ge=0,
            le=65535,
        ),
    ]


class InitializeResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Capabilities supported by the agent.
    agentCapabilities: Annotated[
        Optional[AgentCapabilities],
        Field(description="Capabilities supported by the agent."),
    ] = AgentCapabilities(
        loadSession=False,
        mcpCapabilities=McpCapabilities(http=False, sse=False),
        promptCapabilities=PromptCapabilities(audio=False, embeddedContext=False, image=False),
    )
    # Authentication methods supported by the agent.
    authMethods: Annotated[
        Optional[List[AuthMethod]],
        Field(description="Authentication methods supported by the agent."),
    ] = []
    # The protocol version the client specified if supported by the agent,
    # or the latest protocol version supported by the agent.
    #
    # The client should disconnect, if it doesn't support this version.
    protocolVersion: Annotated[
        int,
        Field(
            description="The protocol version the client specified if supported by the agent,\nor the latest protocol version supported by the agent.\n\nThe client should disconnect, if it doesn't support this version.",
            ge=0,
            le=65535,
        ),
    ]


class KillTerminalCommandRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The session ID for this request.
    sessionId: Annotated[str, Field(description="The session ID for this request.")]
    # The ID of the terminal to kill.
    terminalId: Annotated[str, Field(description="The ID of the terminal to kill.")]


class LoadSessionRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The working directory for this session.
    cwd: Annotated[str, Field(description="The working directory for this session.")]
    # List of MCP servers to connect to for this session.
    mcpServers: Annotated[
        List[Union[HttpMcpServer, SseMcpServer, StdioMcpServer]],
        Field(description="List of MCP servers to connect to for this session."),
    ]
    # The ID of the session to load.
    sessionId: Annotated[str, Field(description="The ID of the session to load.")]


class PermissionOption(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Hint about the nature of this permission option.
    kind: Annotated[PermissionOptionKind, Field(description="Hint about the nature of this permission option.")]
    # Human-readable label to display to the user.
    name: Annotated[str, Field(description="Human-readable label to display to the user.")]
    # Unique identifier for this permission option.
    optionId: Annotated[str, Field(description="Unique identifier for this permission option.")]


class PlanEntry(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Human-readable description of what this task aims to accomplish.
    content: Annotated[
        str,
        Field(description="Human-readable description of what this task aims to accomplish."),
    ]
    # The relative importance of this task.
    # Used to indicate which tasks are most critical to the overall goal.
    priority: Annotated[
        PlanEntryPriority,
        Field(
            description="The relative importance of this task.\nUsed to indicate which tasks are most critical to the overall goal."
        ),
    ]
    # Current execution status of this task.
    status: Annotated[PlanEntryStatus, Field(description="Current execution status of this task.")]


class PromptResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Indicates why the agent stopped processing the turn.
    stopReason: Annotated[StopReason, Field(description="Indicates why the agent stopped processing the turn.")]


class ReadTextFileRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Maximum number of lines to read.
    limit: Annotated[Optional[int], Field(description="Maximum number of lines to read.", ge=0)] = None
    # Line number to start reading from (1-based).
    line: Annotated[
        Optional[int],
        Field(description="Line number to start reading from (1-based).", ge=0),
    ] = None
    # Absolute path to the file to read.
    path: Annotated[str, Field(description="Absolute path to the file to read.")]
    # The session ID for this request.
    sessionId: Annotated[str, Field(description="The session ID for this request.")]


class ReleaseTerminalRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The session ID for this request.
    sessionId: Annotated[str, Field(description="The session ID for this request.")]
    # The ID of the terminal to release.
    terminalId: Annotated[str, Field(description="The ID of the terminal to release.")]


class ResourceLink(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    description: Optional[str] = None
    mimeType: Optional[str] = None
    name: str
    size: Optional[int] = None
    title: Optional[str] = None
    uri: str


class SessionMode(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    description: Optional[str] = None
    # Unique identifier for a Session Mode.
    id: Annotated[str, Field(description="Unique identifier for a Session Mode.")]
    name: str


class SessionModeState(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The set of modes that the Agent can operate in
    availableModes: Annotated[
        List[SessionMode],
        Field(description="The set of modes that the Agent can operate in"),
    ]
    # The current mode the Agent is in.
    currentModeId: Annotated[str, Field(description="The current mode the Agent is in.")]


class AgentPlanUpdate(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The list of tasks to be accomplished.
    #
    # When updating a plan, the agent must send a complete list of all entries
    # with their current status. The client replaces the entire plan with each update.
    entries: Annotated[
        List[PlanEntry],
        Field(
            description="The list of tasks to be accomplished.\n\nWhen updating a plan, the agent must send a complete list of all entries\nwith their current status. The client replaces the entire plan with each update."
        ),
    ]
    sessionUpdate: Literal["plan"]


class AvailableCommandsUpdate(BaseModel):
    availableCommands: List[AvailableCommand]
    sessionUpdate: Literal["available_commands_update"]


class TextContent(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    text: str


class EmbeddedResourceContentBlock(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    # Resource content that can be embedded in a message.
    resource: Annotated[
        Union[TextResourceContents, BlobResourceContents],
        Field(description="Resource content that can be embedded in a message."),
    ]
    type: Literal["resource"]


class EmbeddedResource(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    annotations: Optional[Annotations] = None
    # Resource content that can be embedded in a message.
    resource: Annotated[
        Union[TextResourceContents, BlobResourceContents],
        Field(description="Resource content that can be embedded in a message."),
    ]


class LoadSessionResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # **UNSTABLE**
    #
    # This capability is not part of the spec yet, and may be removed or changed at any point.
    #
    # Initial model state if supported by the Agent
    models: Annotated[
        Optional[SessionModelState],
        Field(
            description="**UNSTABLE**\n\nThis capability is not part of the spec yet, and may be removed or changed at any point.\n\nInitial model state if supported by the Agent"
        ),
    ] = None
    # Initial mode state if supported by the Agent
    #
    # See protocol docs: [Session Modes](https://agentclientprotocol.com/protocol/session-modes)
    modes: Annotated[
        Optional[SessionModeState],
        Field(
            description="Initial mode state if supported by the Agent\n\nSee protocol docs: [Session Modes](https://agentclientprotocol.com/protocol/session-modes)"
        ),
    ] = None


class NewSessionResponse(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # **UNSTABLE**
    #
    # This capability is not part of the spec yet, and may be removed or changed at any point.
    #
    # Initial model state if supported by the Agent
    models: Annotated[
        Optional[SessionModelState],
        Field(
            description="**UNSTABLE**\n\nThis capability is not part of the spec yet, and may be removed or changed at any point.\n\nInitial model state if supported by the Agent"
        ),
    ] = None
    # Initial mode state if supported by the Agent
    #
    # See protocol docs: [Session Modes](https://agentclientprotocol.com/protocol/session-modes)
    modes: Annotated[
        Optional[SessionModeState],
        Field(
            description="Initial mode state if supported by the Agent\n\nSee protocol docs: [Session Modes](https://agentclientprotocol.com/protocol/session-modes)"
        ),
    ] = None
    # Unique identifier for the created session.
    #
    # Used in all subsequent requests for this conversation.
    sessionId: Annotated[
        str,
        Field(
            description="Unique identifier for the created session.\n\nUsed in all subsequent requests for this conversation."
        ),
    ]


class Plan(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The list of tasks to be accomplished.
    #
    # When updating a plan, the agent must send a complete list of all entries
    # with their current status. The client replaces the entire plan with each update.
    entries: Annotated[
        List[PlanEntry],
        Field(
            description="The list of tasks to be accomplished.\n\nWhen updating a plan, the agent must send a complete list of all entries\nwith their current status. The client replaces the entire plan with each update."
        ),
    ]


class PromptRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The blocks of content that compose the user's message.
    #
    # As a baseline, the Agent MUST support [`ContentBlock::Text`] and [`ContentBlock::ResourceLink`],
    # while other variants are optionally enabled via [`PromptCapabilities`].
    #
    # The Client MUST adapt its interface according to [`PromptCapabilities`].
    #
    # The client MAY include referenced pieces of context as either
    # [`ContentBlock::Resource`] or [`ContentBlock::ResourceLink`].
    #
    # When available, [`ContentBlock::Resource`] is preferred
    # as it avoids extra round-trips and allows the message to include
    # pieces of context from sources the agent may not have access to.
    prompt: Annotated[
        List[
            Union[
                TextContentBlock,
                ImageContentBlock,
                AudioContentBlock,
                ResourceContentBlock,
                EmbeddedResourceContentBlock,
            ]
        ],
        Field(
            description="The blocks of content that compose the user's message.\n\nAs a baseline, the Agent MUST support [`ContentBlock::Text`] and [`ContentBlock::ResourceLink`],\nwhile other variants are optionally enabled via [`PromptCapabilities`].\n\nThe Client MUST adapt its interface according to [`PromptCapabilities`].\n\nThe client MAY include referenced pieces of context as either\n[`ContentBlock::Resource`] or [`ContentBlock::ResourceLink`].\n\nWhen available, [`ContentBlock::Resource`] is preferred\nas it avoids extra round-trips and allows the message to include\npieces of context from sources the agent may not have access to."
        ),
    ]
    # The ID of the session to send this user message to
    sessionId: Annotated[str, Field(description="The ID of the session to send this user message to")]


class UserMessageChunk(BaseModel):
    # Content blocks represent displayable information in the Agent Client Protocol.
    #
    # They provide a structured way to handle various types of user-facing content—whether
    # it's text from language models, images for analysis, or embedded resources for context.
    #
    # Content blocks appear in:
    # - User prompts sent via `session/prompt`
    # - Language model output streamed through `session/update` notifications
    # - Progress updates and results from tool calls
    #
    # This structure is compatible with the Model Context Protocol (MCP), enabling
    # agents to seamlessly forward content from MCP tool outputs without transformation.
    #
    # See protocol docs: [Content](https://agentclientprotocol.com/protocol/content)
    content: Annotated[
        Union[
            TextContentBlock, ImageContentBlock, AudioContentBlock, ResourceContentBlock, EmbeddedResourceContentBlock
        ],
        Field(
            description="Content blocks represent displayable information in the Agent Client Protocol.\n\nThey provide a structured way to handle various types of user-facing content—whether\nit's text from language models, images for analysis, or embedded resources for context.\n\nContent blocks appear in:\n- User prompts sent via `session/prompt`\n- Language model output streamed through `session/update` notifications\n- Progress updates and results from tool calls\n\nThis structure is compatible with the Model Context Protocol (MCP), enabling\nagents to seamlessly forward content from MCP tool outputs without transformation.\n\nSee protocol docs: [Content](https://agentclientprotocol.com/protocol/content)"
        ),
    ]
    sessionUpdate: Literal["user_message_chunk"]


class AgentMessageChunk(BaseModel):
    # Content blocks represent displayable information in the Agent Client Protocol.
    #
    # They provide a structured way to handle various types of user-facing content—whether
    # it's text from language models, images for analysis, or embedded resources for context.
    #
    # Content blocks appear in:
    # - User prompts sent via `session/prompt`
    # - Language model output streamed through `session/update` notifications
    # - Progress updates and results from tool calls
    #
    # This structure is compatible with the Model Context Protocol (MCP), enabling
    # agents to seamlessly forward content from MCP tool outputs without transformation.
    #
    # See protocol docs: [Content](https://agentclientprotocol.com/protocol/content)
    content: Annotated[
        Union[
            TextContentBlock, ImageContentBlock, AudioContentBlock, ResourceContentBlock, EmbeddedResourceContentBlock
        ],
        Field(
            description="Content blocks represent displayable information in the Agent Client Protocol.\n\nThey provide a structured way to handle various types of user-facing content—whether\nit's text from language models, images for analysis, or embedded resources for context.\n\nContent blocks appear in:\n- User prompts sent via `session/prompt`\n- Language model output streamed through `session/update` notifications\n- Progress updates and results from tool calls\n\nThis structure is compatible with the Model Context Protocol (MCP), enabling\nagents to seamlessly forward content from MCP tool outputs without transformation.\n\nSee protocol docs: [Content](https://agentclientprotocol.com/protocol/content)"
        ),
    ]
    sessionUpdate: Literal["agent_message_chunk"]


class AgentThoughtChunk(BaseModel):
    # Content blocks represent displayable information in the Agent Client Protocol.
    #
    # They provide a structured way to handle various types of user-facing content—whether
    # it's text from language models, images for analysis, or embedded resources for context.
    #
    # Content blocks appear in:
    # - User prompts sent via `session/prompt`
    # - Language model output streamed through `session/update` notifications
    # - Progress updates and results from tool calls
    #
    # This structure is compatible with the Model Context Protocol (MCP), enabling
    # agents to seamlessly forward content from MCP tool outputs without transformation.
    #
    # See protocol docs: [Content](https://agentclientprotocol.com/protocol/content)
    content: Annotated[
        Union[
            TextContentBlock, ImageContentBlock, AudioContentBlock, ResourceContentBlock, EmbeddedResourceContentBlock
        ],
        Field(
            description="Content blocks represent displayable information in the Agent Client Protocol.\n\nThey provide a structured way to handle various types of user-facing content—whether\nit's text from language models, images for analysis, or embedded resources for context.\n\nContent blocks appear in:\n- User prompts sent via `session/prompt`\n- Language model output streamed through `session/update` notifications\n- Progress updates and results from tool calls\n\nThis structure is compatible with the Model Context Protocol (MCP), enabling\nagents to seamlessly forward content from MCP tool outputs without transformation.\n\nSee protocol docs: [Content](https://agentclientprotocol.com/protocol/content)"
        ),
    ]
    sessionUpdate: Literal["agent_thought_chunk"]


class ContentToolCallContent(BaseModel):
    # The actual content block.
    content: Annotated[
        Union[
            TextContentBlock, ImageContentBlock, AudioContentBlock, ResourceContentBlock, EmbeddedResourceContentBlock
        ],
        Field(description="The actual content block."),
    ]
    type: Literal["content"]


class ToolCallUpdate(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Replace the content collection.
    content: Annotated[
        Optional[List[Union[ContentToolCallContent, FileEditToolCallContent, TerminalToolCallContent]]],
        Field(description="Replace the content collection."),
    ] = None
    # Update the tool kind.
    kind: Annotated[Optional[ToolKind], Field(description="Update the tool kind.")] = None
    # Replace the locations collection.
    locations: Annotated[
        Optional[List[ToolCallLocation]],
        Field(description="Replace the locations collection."),
    ] = None
    # Update the raw input.
    rawInput: Annotated[Optional[Any], Field(description="Update the raw input.")] = None
    # Update the raw output.
    rawOutput: Annotated[Optional[Any], Field(description="Update the raw output.")] = None
    # Update the execution status.
    status: Annotated[Optional[ToolCallStatus], Field(description="Update the execution status.")] = None
    # Update the human-readable title.
    title: Annotated[Optional[str], Field(description="Update the human-readable title.")] = None
    # The ID of the tool call being updated.
    toolCallId: Annotated[str, Field(description="The ID of the tool call being updated.")]


class RequestPermissionRequest(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Available permission options for the user to choose from.
    options: Annotated[
        List[PermissionOption],
        Field(description="Available permission options for the user to choose from."),
    ]
    # The session ID for this request.
    sessionId: Annotated[str, Field(description="The session ID for this request.")]
    # Details about the tool call requiring permission.
    toolCall: Annotated[
        ToolCallUpdate,
        Field(description="Details about the tool call requiring permission."),
    ]


class ToolCallStart(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Content produced by the tool call.
    content: Annotated[
        Optional[List[Union[ContentToolCallContent, FileEditToolCallContent, TerminalToolCallContent]]],
        Field(description="Content produced by the tool call."),
    ] = None
    # The category of tool being invoked.
    # Helps clients choose appropriate icons and UI treatment.
    kind: Annotated[
        Optional[ToolKind],
        Field(
            description="The category of tool being invoked.\nHelps clients choose appropriate icons and UI treatment."
        ),
    ] = None
    # File locations affected by this tool call.
    # Enables "follow-along" features in clients.
    locations: Annotated[
        Optional[List[ToolCallLocation]],
        Field(description='File locations affected by this tool call.\nEnables "follow-along" features in clients.'),
    ] = None
    # Raw input parameters sent to the tool.
    rawInput: Annotated[Optional[Any], Field(description="Raw input parameters sent to the tool.")] = None
    # Raw output returned by the tool.
    rawOutput: Annotated[Optional[Any], Field(description="Raw output returned by the tool.")] = None
    sessionUpdate: Literal["tool_call"]
    # Current execution status of the tool call.
    status: Annotated[Optional[ToolCallStatus], Field(description="Current execution status of the tool call.")] = None
    # Human-readable title describing what the tool is doing.
    title: Annotated[
        str,
        Field(description="Human-readable title describing what the tool is doing."),
    ]
    # Unique identifier for this tool call within the session.
    toolCallId: Annotated[
        str,
        Field(description="Unique identifier for this tool call within the session."),
    ]


class ToolCallProgress(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Replace the content collection.
    content: Annotated[
        Optional[List[Union[ContentToolCallContent, FileEditToolCallContent, TerminalToolCallContent]]],
        Field(description="Replace the content collection."),
    ] = None
    # Update the tool kind.
    kind: Annotated[Optional[ToolKind], Field(description="Update the tool kind.")] = None
    # Replace the locations collection.
    locations: Annotated[
        Optional[List[ToolCallLocation]],
        Field(description="Replace the locations collection."),
    ] = None
    # Update the raw input.
    rawInput: Annotated[Optional[Any], Field(description="Update the raw input.")] = None
    # Update the raw output.
    rawOutput: Annotated[Optional[Any], Field(description="Update the raw output.")] = None
    sessionUpdate: Literal["tool_call_update"]
    # Update the execution status.
    status: Annotated[Optional[ToolCallStatus], Field(description="Update the execution status.")] = None
    # Update the human-readable title.
    title: Annotated[Optional[str], Field(description="Update the human-readable title.")] = None
    # The ID of the tool call being updated.
    toolCallId: Annotated[str, Field(description="The ID of the tool call being updated.")]


class ToolCall(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # Content produced by the tool call.
    content: Annotated[
        Optional[List[Union[ContentToolCallContent, FileEditToolCallContent, TerminalToolCallContent]]],
        Field(description="Content produced by the tool call."),
    ] = None
    # The category of tool being invoked.
    # Helps clients choose appropriate icons and UI treatment.
    kind: Annotated[
        Optional[ToolKind],
        Field(
            description="The category of tool being invoked.\nHelps clients choose appropriate icons and UI treatment."
        ),
    ] = None
    # File locations affected by this tool call.
    # Enables "follow-along" features in clients.
    locations: Annotated[
        Optional[List[ToolCallLocation]],
        Field(description='File locations affected by this tool call.\nEnables "follow-along" features in clients.'),
    ] = None
    # Raw input parameters sent to the tool.
    rawInput: Annotated[Optional[Any], Field(description="Raw input parameters sent to the tool.")] = None
    # Raw output returned by the tool.
    rawOutput: Annotated[Optional[Any], Field(description="Raw output returned by the tool.")] = None
    # Current execution status of the tool call.
    status: Annotated[Optional[ToolCallStatus], Field(description="Current execution status of the tool call.")] = None
    # Human-readable title describing what the tool is doing.
    title: Annotated[
        str,
        Field(description="Human-readable title describing what the tool is doing."),
    ]
    # Unique identifier for this tool call within the session.
    toolCallId: Annotated[
        str,
        Field(description="Unique identifier for this tool call within the session."),
    ]


class SessionNotification(BaseModel):
    # Extension point for implementations
    field_meta: Annotated[
        Optional[Any],
        Field(alias="_meta", description="Extension point for implementations"),
    ] = None
    # The ID of the session this update pertains to.
    sessionId: Annotated[str, Field(description="The ID of the session this update pertains to.")]
    # The actual update content.
    update: Annotated[
        Union[
            UserMessageChunk,
            AgentMessageChunk,
            AgentThoughtChunk,
            ToolCallStart,
            ToolCallProgress,
            AgentPlanUpdate,
            AvailableCommandsUpdate,
            CurrentModeUpdate,
        ],
        Field(description="The actual update content."),
    ]


class Model(
    RootModel[
        Union[
            Union[
                WriteTextFileRequest,
                ReadTextFileRequest,
                RequestPermissionRequest,
                CreateTerminalRequest,
                TerminalOutputRequest,
                ReleaseTerminalRequest,
                WaitForTerminalExitRequest,
                KillTerminalCommandRequest,
                Any,
            ],
            Union[
                WriteTextFileResponse,
                ReadTextFileResponse,
                RequestPermissionResponse,
                CreateTerminalResponse,
                TerminalOutputResponse,
                ReleaseTerminalResponse,
                WaitForTerminalExitResponse,
                KillTerminalCommandResponse,
                Any,
            ],
            Union[CancelNotification, Any],
            Union[
                InitializeRequest,
                AuthenticateRequest,
                NewSessionRequest,
                LoadSessionRequest,
                SetSessionModeRequest,
                PromptRequest,
                SetSessionModelRequest,
                Any,
            ],
            Union[
                InitializeResponse,
                AuthenticateResponse,
                NewSessionResponse,
                LoadSessionResponse,
                SetSessionModeResponse,
                PromptResponse,
                SetSessionModelResponse,
                Any,
            ],
            Union[SessionNotification, Any],
        ]
    ]
):
    root: Union[
        Union[
            WriteTextFileRequest,
            ReadTextFileRequest,
            RequestPermissionRequest,
            CreateTerminalRequest,
            TerminalOutputRequest,
            ReleaseTerminalRequest,
            WaitForTerminalExitRequest,
            KillTerminalCommandRequest,
            Any,
        ],
        Union[
            WriteTextFileResponse,
            ReadTextFileResponse,
            RequestPermissionResponse,
            CreateTerminalResponse,
            TerminalOutputResponse,
            ReleaseTerminalResponse,
            WaitForTerminalExitResponse,
            KillTerminalCommandResponse,
            Any,
        ],
        Union[CancelNotification, Any],
        Union[
            InitializeRequest,
            AuthenticateRequest,
            NewSessionRequest,
            LoadSessionRequest,
            SetSessionModeRequest,
            PromptRequest,
            SetSessionModelRequest,
            Any,
        ],
        Union[
            InitializeResponse,
            AuthenticateResponse,
            NewSessionResponse,
            LoadSessionResponse,
            SetSessionModeResponse,
            PromptResponse,
            SetSessionModelResponse,
            Any,
        ],
        Union[SessionNotification, Any],
    ]


# Backwards compatibility aliases
AvailableCommandInput1 = CommandInputHint
ContentBlock1 = TextContentBlock
ContentBlock2 = ImageContentBlock
ContentBlock3 = AudioContentBlock
ContentBlock4 = ResourceContentBlock
ContentBlock5 = EmbeddedResourceContentBlock
McpServer1 = HttpMcpServer
McpServer2 = SseMcpServer
McpServer3 = StdioMcpServer
RequestPermissionOutcome1 = DeniedOutcome
RequestPermissionOutcome2 = AllowedOutcome
SessionUpdate1 = UserMessageChunk
SessionUpdate2 = AgentMessageChunk
SessionUpdate3 = AgentThoughtChunk
SessionUpdate4 = ToolCallStart
SessionUpdate5 = ToolCallProgress
SessionUpdate6 = AgentPlanUpdate
SessionUpdate7 = AvailableCommandsUpdate
SessionUpdate8 = CurrentModeUpdate
ToolCallContent1 = ContentToolCallContent
ToolCallContent2 = FileEditToolCallContent
ToolCallContent3 = TerminalToolCallContent

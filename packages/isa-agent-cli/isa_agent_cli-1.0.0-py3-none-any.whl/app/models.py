"""
Data models for the Enhanced MCP Client with Rich Media Support
"""
from typing import Dict, List, Any, Optional, Union, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Streaming Event Models
class EventType(str, Enum):
    """Types of streaming events"""
    CONNECTION = "connection"
    MCP_DISCOVERY = "mcp_discovery"
    AGENT_START = "agent_start"
    MODEL_CALL = "model_call"
    MODEL_RESPONSE = "model_response"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    HUMAN_INPUT_REQUEST = "human_input_request"
    HUMAN_INPUT_RESPONSE = "human_input_response"
    AUTHORIZATION_REQUEST = "authorization_request"
    AUTHORIZATION_response = "authorization_response"
    PROGRESS_UPDATE = "progress_update"
    ERROR = "error"
    COMPLETION = "completion"
    DEBUG = "debug"

class StreamingEvent(BaseModel):
    """Base streaming event model"""
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.now)
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now().timestamp()}")
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConnectionEvent(StreamingEvent):
    """Connection-related events"""
    event_type: Literal[EventType.CONNECTION] = EventType.CONNECTION
    connection_status: Literal["connecting", "connected", "disconnected", "failed"]
    connection_url: Optional[str] = None
    connection_type: Optional[str] = None  # "load_balanced", "direct"

class MCPDiscoveryEvent(StreamingEvent):
    """MCP capability discovery events"""
    event_type: Literal[EventType.MCP_DISCOVERY] = EventType.MCP_DISCOVERY
    capabilities: Dict[str, Any]
    tools_count: int = 0
    resources_count: int = 0
    prompts_count: int = 0

class AgentStartEvent(StreamingEvent):
    """Agent workflow start events"""
    event_type: Literal[EventType.AGENT_START] = EventType.AGENT_START
    user_query: str
    thread_id: str
    workflow_type: str = "langgraph"

class ModelCallEvent(StreamingEvent):
    """Language model call events"""
    event_type: Literal[EventType.MODEL_CALL] = EventType.MODEL_CALL
    model_name: str
    input_tokens: Optional[int] = None
    available_tools_count: int = 0

class ModelResponseEvent(StreamingEvent):
    """Language model response events"""
    event_type: Literal[EventType.MODEL_RESPONSE] = EventType.MODEL_RESPONSE
    response_preview: str  # First 100 chars
    has_tool_calls: bool = False
    tool_calls_count: int = 0
    output_tokens: Optional[int] = None

class ToolCallEvent(StreamingEvent):
    """Tool call events"""
    event_type: Literal[EventType.TOOL_CALL] = EventType.TOOL_CALL
    tool_name: str
    tool_args: Dict[str, Any]
    call_id: Optional[str] = None

class ToolResultEvent(StreamingEvent):
    """Tool result events"""
    event_type: Literal[EventType.TOOL_RESULT] = EventType.TOOL_RESULT
    tool_name: str
    result_preview: str  # First 100 chars
    success: bool = True
    call_id: Optional[str] = None

class HumanInputRequestEvent(StreamingEvent):
    """Human input request events"""
    event_type: Literal[EventType.HUMAN_INPUT_REQUEST] = EventType.HUMAN_INPUT_REQUEST
    question: str
    context: Optional[str] = None
    request_id: str
    input_type: Literal["text", "choice", "confirmation"] = "text"
    choices: Optional[List[str]] = None

class HumanInputResponseEvent(StreamingEvent):
    """Human input response events"""
    event_type: Literal[EventType.HUMAN_INPUT_RESPONSE] = EventType.HUMAN_INPUT_RESPONSE
    request_id: str
    response: str
    response_time: Optional[float] = None

class AuthorizationRequestEvent(StreamingEvent):
    """Authorization request events"""
    event_type: Literal[EventType.AUTHORIZATION_REQUEST] = EventType.AUTHORIZATION_REQUEST
    tool_name: str
    reason: str
    security_level: str
    request_id: str
    tool_args: Dict[str, Any]
    impact_assessment: Optional[str] = None

class AuthorizationResponseEvent(StreamingEvent):
    """Authorization response events"""
    event_type: Literal[EventType.AUTHORIZATION_response] = EventType.AUTHORIZATION_response
    request_id: str
    approved: bool
    approved_by: str
    response_time: Optional[float] = None

class ProgressUpdateEvent(StreamingEvent):
    """Progress update events"""
    event_type: Literal[EventType.PROGRESS_UPDATE] = EventType.PROGRESS_UPDATE
    stage: str
    progress_percent: Optional[int] = None
    current_step: str
    total_steps: Optional[int] = None

class ErrorEvent(StreamingEvent):
    """Error events"""
    event_type: Literal[EventType.ERROR] = EventType.ERROR
    error_type: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    recoverable: bool = True

class CompletionEvent(StreamingEvent):
    """Completion events"""
    event_type: Literal[EventType.COMPLETION] = EventType.COMPLETION
    final_response: str
    total_time: Optional[float] = None
    tokens_used: Optional[int] = None
    tools_called: int = 0

class DebugEvent(StreamingEvent):
    """Debug events for development"""
    event_type: Literal[EventType.DEBUG] = EventType.DEBUG
    debug_message: str
    debug_data: Optional[Dict[str, Any]] = None

# Union type for all streaming events
StreamingEventUnion = Union[
    ConnectionEvent, MCPDiscoveryEvent, AgentStartEvent,
    ModelCallEvent, ModelResponseEvent, ToolCallEvent, ToolResultEvent,
    HumanInputRequestEvent, HumanInputResponseEvent,
    AuthorizationRequestEvent, AuthorizationResponseEvent,
    ProgressUpdateEvent, ErrorEvent, CompletionEvent, DebugEvent
]

# Streaming Response Models (using string forward references)
class StreamingChatRequest(BaseModel):
    """Streaming chat request"""
    message: Union[str, List["ContentBlock"]]
    thread_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    stream_events: bool = True
    event_filter: Optional[List[EventType]] = None  # Filter specific event types

class StreamCreateRequest(BaseModel):
    """Request to create a new streaming chat session"""
    thread_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class StreamingChatResponse(BaseModel):
    """Streaming chat response metadata"""
    thread_id: str
    stream_id: str
    started_at: datetime
    estimated_duration: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Rich Media Content Types
class ContentType(str, Enum):
    """Supported content types for rich media"""
    TEXT = "text"
    IMAGE = "image" 
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    CODE = "code"
    TABLE = "table"
    CHART = "chart"
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "markdown"

class MediaType(str, Enum):
    """Media file types"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    OTHER = "other"

# Base Content Block
class BaseContentBlock(BaseModel):
    """Base class for all content blocks"""
    type: ContentType
    id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Specific Content Blocks
class TextBlock(BaseContentBlock):
    """Text content block"""
    type: Literal[ContentType.TEXT] = ContentType.TEXT
    content: str
    format: Optional[Literal["plain", "markdown", "html"]] = "plain"

class ImageBlock(BaseContentBlock):
    """Image content block"""
    type: Literal[ContentType.IMAGE] = ContentType.IMAGE
    url: str
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    caption: Optional[str] = None

class AudioBlock(BaseContentBlock):
    """Audio content block"""
    type: Literal[ContentType.AUDIO] = ContentType.AUDIO
    url: str
    duration: Optional[float] = None
    transcript: Optional[str] = None
    format: Optional[str] = None

class VideoBlock(BaseContentBlock):
    """Video content block"""
    type: Literal[ContentType.VIDEO] = ContentType.VIDEO
    url: str
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None

class FileBlock(BaseContentBlock):
    """File content block"""
    type: Literal[ContentType.FILE] = ContentType.FILE
    url: str
    filename: str
    size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None

class CodeBlock(BaseContentBlock):
    """Code content block"""
    type: Literal[ContentType.CODE] = ContentType.CODE
    content: str
    language: Optional[str] = None
    filename: Optional[str] = None
    line_numbers: bool = False

class TableBlock(BaseContentBlock):
    """Table content block"""
    type: Literal[ContentType.TABLE] = ContentType.TABLE
    headers: List[str]
    rows: List[List[str]]
    caption: Optional[str] = None

class ChartBlock(BaseContentBlock):
    """Chart/Graph content block"""
    type: Literal[ContentType.CHART] = ContentType.CHART
    chart_type: Literal["bar", "line", "pie", "scatter", "area"] = "bar"
    data: Dict[str, Any]
    title: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None

# Union type for all content blocks
ContentBlock = Union[
    TextBlock, ImageBlock, AudioBlock, VideoBlock, 
    FileBlock, CodeBlock, TableBlock, ChartBlock
]

# Rich Message Model
class RichMessage(BaseModel):
    """Rich message supporting multiple content types"""
    role: Literal["user", "assistant", "system"] = "user"
    content: Union[str, List[ContentBlock]]
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# API Request/Response Models
class ConversationRequest(BaseModel):
    """Rich conversation request supporting multiple input types"""
    message: Union[str, List[ContentBlock]]
    thread_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    media_files: Optional[List[str]] = None  # URLs or file IDs
    preferences: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    """Rich conversation response with multiple content types"""
    response: Union[str, List[ContentBlock]]
    thread_id: str
    metadata: Optional[Dict[str, Any]] = None
    media_generated: Optional[List[str]] = None  # Generated media URLs
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
# File Upload Models
class FileUploadRequest(BaseModel):
    """File upload request"""
    filename: str
    content_type: str
    size: int
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class FileUploadResponse(BaseModel):
    """File upload response"""
    file_id: str
    url: str
    filename: str
    content_type: str
    size: int
    upload_time: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MediaItem(BaseModel):
    """Media item information"""
    id: str
    type: MediaType
    url: str
    name: str
    mime_type: str
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    thumbnail_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Existing models (keeping for backward compatibility)
class SessionInfo(BaseModel):
    """Session information"""
    thread_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SessionListResponse(BaseModel):
    """List of sessions response"""
    sessions: List[SessionInfo]
    total: int

class MCPCapabilities(BaseModel):
    """MCP server capabilities"""
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    prompts: List[Dict[str, Any]] = Field(default_factory=list)

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    mcp_connected: bool
    timestamp: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    details: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Agent State for LangGraph (using TypedDict for LangGraph compatibility)
class AgentState(TypedDict):
    """Agent state for LangGraph workflow - using TypedDict for proper LangGraph support"""
    messages: List[Any]
    user_query: str
    available_tools: List[Dict[str, Any]]
    available_resources: List[Dict[str, Any]]
    available_prompts: List[Dict[str, Any]]
    current_step: str
    next_action: str
    mcp_session: Any
    trace_id: Optional[str]  # 添加trace_id字段
    llm_cost_info: Optional[Dict[str, Any]]  # 添加成本信息字段 
"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message model."""
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, description="User message")
    conversation_id: Optional[str] = None
    stream: bool = True


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    conversation_id: str
    component: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}


class StreamEvent(BaseModel):
    """Streaming event model."""
    type: Literal["text", "component", "tool_call", "error", "done"]
    content: Optional[str] = None
    component: Optional[str] = None
    props: Optional[Dict[str, Any]] = None
    tool: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    ollama_connected: bool = False


class MCPServerInfo(BaseModel):
    """MCP server information."""
    name: str
    enabled: bool
    description: str
    tools: List[str] = []


class MCPServerListResponse(BaseModel):
    """MCP server list response."""
    servers: List[MCPServerInfo]


class MCPServerActionRequest(BaseModel):
    """MCP server action request."""
    action: Literal["start", "stop", "restart"]


class MCPServerActionResponse(BaseModel):
    """MCP server action response."""
    success: bool
    message: str
    server_name: str

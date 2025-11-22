"""MCP router for server and tool management."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ServerEnableRequest(BaseModel):
    """Server enable/disable request."""
    server_name: str
    enabled: bool


class ToolCallRequest(BaseModel):
    """Tool call request."""
    tool_name: str
    parameters: Dict[str, Any]


def get_mcp_service():
    """Get the global MCP service instance."""
    from main import mcp_service
    if mcp_service is None:
        raise HTTPException(status_code=503, detail="MCP service not initialized")
    return mcp_service


@router.get("/servers")
async def list_servers():
    """List all configured MCP servers."""
    try:
        mcp = get_mcp_service()
        servers = mcp.list_servers()
        return {
            "servers": servers,
            "count": len(servers)
        }
    except Exception as e:
        logger.error(f"Failed to list MCP servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/toggle")
async def toggle_server(request: ServerEnableRequest):
    """Enable or disable an MCP server."""
    try:
        mcp = get_mcp_service()

        if request.enabled:
            success = await mcp.enable_server(request.server_name)
            action = "enabled"
        else:
            success = await mcp.disable_server(request.server_name)
            action = "disabled"

        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to {action} server: {request.server_name}"
            )

        return {
            "success": True,
            "message": f"Server {request.server_name} {action}",
            "server_name": request.server_name,
            "enabled": request.enabled
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def list_tools():
    """List available tools from enabled MCP servers."""
    try:
        mcp = get_mcp_service()
        tools = mcp.get_available_tools()
        return {
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        logger.error(f"Failed to list MCP tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """Call an MCP tool."""
    try:
        mcp = get_mcp_service()
        result = await mcp.call_tool(request.tool_name, request.parameters)

        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Tool call failed')
            )

        return {
            "success": True,
            "tool": request.tool_name,
            **result  # Return all result data (result, items, files, content, etc.)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to call tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

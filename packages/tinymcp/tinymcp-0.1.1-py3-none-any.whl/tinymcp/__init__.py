"""
Copyright 2025 Grabtaxi Holdings Pte Ltd (GRAB), All rights reserved.
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file
"""

"""
Tiny MCP - A lightweight, auth-agnostic MCP implementation.

This package provides:
- @mcp_tool decorator for automatic tool registration
- Built-in serialization for complex objects
- FastAPI router integration
- Zero auth dependencies (bring your own auth)
"""

from tinymcp.registry import ToolRegistry, mcp_tool, get_default_registry
from tinymcp.router import create_mcp_router

__version__ = "0.1.1"
__all__ = ["ToolRegistry", "mcp_tool", "get_default_registry", "create_mcp_router"]

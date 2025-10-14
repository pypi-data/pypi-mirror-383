from __future__ import annotations

# Public SDK surface for widgets in FastMCP, optimized for OpenAI Apps SDK.

from .widgets import (
    WidgetToolResponse,
    build_widget_tool_response,
    register_widget_resource,
    register_widget_tool,
    register_decorated_widgets,
    widget,
)

__all__ = [
    "WidgetToolResponse",
    "build_widget_tool_response",
    "register_widget_resource",
    "register_widget_tool",
    "register_decorated_widgets",
    "widget",
]


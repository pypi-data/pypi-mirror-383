from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Sequence

from fastmcp import FastMCP
from fastmcp.tools import Tool

WidgetToolResponse = Dict[str, Any]

_DEFAULT_CSP_RESOURCES: Sequence[str] = ("https://persistent.oaistatic.com",)
_DEFAULT_RESOURCE_ANNOTATIONS: Mapping[str, Any] = {
    "readOnlyHint": True,
    "idempotentHint": True,
}
_DEFAULT_TOOL_ANNOTATIONS: Mapping[str, Any] = {
    "destructiveHint": False,
    "openWorldHint": False,
    "readOnlyHint": True,
}


def build_widget_tool_response(
    response_text: str | None = None,
    structured_content: Dict[str, Any] | None = None,
) -> WidgetToolResponse:
    """Helper for building standardized widget tool payloads."""

    content = (
        [
            {
                "type": "text",
                "text": response_text,
            }
        ]
        if response_text
        else []
    )

    return {"content": content, "structuredContent": structured_content or {}}


@dataclass
class WidgetRegistration:
    """Stores a decorated widget function until it is bound to an MCP instance."""

    base_callable: Callable[..., Any]
    config: Dict[str, Any]
    base_name: str | None = None
    description: str | None = None
    annotations: Mapping[str, Any] | None = None
    meta: Mapping[str, Any] | None = None
    tool_annotations: Mapping[str, Any] | None = None
    widget_accessible: bool | None = None
    result_can_produce_widget: bool | None = None
    register_resource: bool = True
    resource_name: str | None = None
    resource_description: str | None = None
    resource_annotations: Mapping[str, Any] | None = None
    _is_registered: bool = field(default=False, init=False, repr=False)


_WIDGET_REGISTRY: List[WidgetRegistration] = []


def _normalize_sequence(seq: Sequence[str] | None, default: Sequence[str]) -> List[str]:
    return list(seq if seq is not None else default)


def _build_widget_meta(config: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "openai/widgetDescription": config.get("widget_description")
        or f"{config['title']} widget UI.",
        "openai/widgetPrefersBorder": config.get("widget_prefers_border", True),
        "openai/widgetCSP": {
            "resource_domains": _normalize_sequence(
                config.get("widget_csp_resources"),
                _DEFAULT_CSP_RESOURCES,
            ),
            "connect_domains": _normalize_sequence(
                config.get("widget_csp_connect"),
                (),
            ),
        },
    }


def _embedded_widget_resource(config: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "type": "resource",
        "resource": {
            "type": "text",
            "uri": config["template_uri"],
            "mimeType": config.get("mime_type", "text/html+skybridge"),
            "text": config["html"],
            "title": config["title"],
            "_meta": _build_widget_meta(config),
        },
    }


def _build_tool_meta(
    config: Mapping[str, Any],
    *,
    widget_accessible: bool | None = None,
    result_can_produce_widget: bool | None = None,
) -> Dict[str, Any]:
    meta = {
        "openai.com/widget": _embedded_widget_resource(config),
        "openai/outputTemplate": config["template_uri"],
        "openai/toolInvocation/invoking": config["invoking"],
        "openai/toolInvocation/invoked": config["invoked"],
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }

    if widget_accessible is not None:
        meta["openai/widgetAccessible"] = widget_accessible
    if result_can_produce_widget is not None:
        meta["openai/resultCanProduceWidget"] = result_can_produce_widget

    return meta


def _default_tool_annotations(
    tool_annotations: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    combined = dict(_DEFAULT_TOOL_ANNOTATIONS)
    if tool_annotations:
        combined.update(tool_annotations)
    return combined


def register_widget_resource(
    mcp: FastMCP,
    config: Mapping[str, Any],
    *,
    name: str | None = None,
    description: str | None = None,
    annotations: Mapping[str, Any] | None = None,
) -> Callable[[], str]:
    """Expose widget HTML via FastMCP's @resource decorator."""

    resource_name = name or config["title"]
    resource_description = description or f"{config['title']} widget markup"

    @mcp.resource(
        uri=config["template_uri"],
        name=resource_name,
        description=resource_description,
        mime_type=config.get("mime_type", "text/html+skybridge"),
        annotations=annotations or _DEFAULT_RESOURCE_ANNOTATIONS,
        meta=_build_widget_meta(config),
    )
    def _widget_resource() -> str:
        return config["html"]

    return _widget_resource


def register_widget_tool(
    mcp: FastMCP,
    *,
    base_tool: Callable[..., Any],
    config: Mapping[str, Any],
    description: str | None = None,
    annotations: Mapping[str, Any] | None = None,
    meta: Mapping[str, Any] | None = None,
    tool_annotations: Mapping[str, Any] | None = None,
    widget_accessible: bool | None = None,
    result_can_produce_widget: bool | None = None,
) -> Tool:
    """Register a transformed widget tool around a normalizing base handler."""

    combined_annotations = _default_tool_annotations(tool_annotations)
    if annotations:
        combined_annotations.update(annotations)

    tool_meta = _build_tool_meta(
        config,
        widget_accessible=widget_accessible,
        result_can_produce_widget=result_can_produce_widget,
    )
    if meta:
        tool_meta.update(meta)

    transformed = Tool.from_tool(
        base_tool,
        name=config["identifier"],
        description=description or config["title"],
        annotations=combined_annotations,
        meta=tool_meta,
    )

    base_tool.disable()
    mcp.add_tool(transformed)
    return transformed


def widget(
    *,
    identifier: str,
    title: str,
    template_uri: str,
    invoking: str,
    invoked: str,
    html: str,
    mime_type: str = "text/html+skybridge",
    widget_description: str | None = None,
    widget_prefers_border: bool = True,
    widget_csp_resources: Sequence[str] | None = None,
    widget_csp_connect: Sequence[str] | None = None,
    base_name: str | None = None,
    description: str | None = None,
    annotations: Mapping[str, Any] | None = None,
    meta: Mapping[str, Any] | None = None,
    tool_annotations: Mapping[str, Any] | None = None,
    widget_accessible: bool | None = None,
    result_can_produce_widget: bool | None = None,
    register_resource: bool = True,
    resource_name: str | None = None,
    resource_description: str | None = None,
    resource_annotations: Mapping[str, Any] | None = None,
    mcp: FastMCP | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register a widget tool and matching resource for ChatGPT components.

    See README for guidance on identifiers, CSP hints, and output templates.
    """

    config = {
        "identifier": identifier,
        "title": title,
        "template_uri": template_uri,
        "invoking": invoking,
        "invoked": invoked,
        "html": html,
        "mime_type": mime_type,
        "widget_description": widget_description,
        "widget_prefers_border": widget_prefers_border,
        "widget_csp_resources": tuple(
            widget_csp_resources if widget_csp_resources is not None else _DEFAULT_CSP_RESOURCES
        ),
        "widget_csp_connect": tuple(widget_csp_connect or ()),
    }

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        registration = WidgetRegistration(
            base_callable=func,
            config=config,
            base_name=base_name,
            description=description,
            annotations=annotations,
            meta=meta,
            tool_annotations=tool_annotations,
            widget_accessible=widget_accessible,
            result_can_produce_widget=result_can_produce_widget,
            register_resource=register_resource,
            resource_name=resource_name,
            resource_description=resource_description,
            resource_annotations=resource_annotations,
        )

        _WIDGET_REGISTRY.append(registration)

        if mcp is not None:
            _register_decorated_widget(mcp, registration)

        return func

    return decorator


def register_decorated_widgets(mcp: FastMCP) -> None:
    """Bind every decorated widget function to the supplied FastMCP instance."""

    for registration in _WIDGET_REGISTRY:
        _register_decorated_widget(mcp, registration)


def _register_decorated_widget(mcp: FastMCP, registration: WidgetRegistration) -> None:
    """Idempotently register a widget decoration with the provided MCP."""

    if registration._is_registered:
        return

    base_name = registration.base_name or f"_{registration.config['identifier']}_base"

    if registration.register_resource:
        register_widget_resource(
            mcp,
            registration.config,
            name=registration.resource_name,
            description=registration.resource_description,
            annotations=registration.resource_annotations,
        )

    base_tool = mcp.tool(name=base_name)(registration.base_callable)

    register_widget_tool(
        mcp,
        base_tool=base_tool,
        config=registration.config,
        description=registration.description,
        annotations=registration.annotations,
        meta=registration.meta,
        tool_annotations=registration.tool_annotations,
        widget_accessible=registration.widget_accessible,
        result_can_produce_widget=registration.result_can_produce_widget,
    )

    registration._is_registered = True


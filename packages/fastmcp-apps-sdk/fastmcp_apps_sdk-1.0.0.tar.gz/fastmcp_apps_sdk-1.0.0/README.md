# fastmcp-apps-sdk

Widgets SDK for FastMCP targeting OpenAI Apps SDK. It provides a simple `@widget(...)` decorator and helpers to:

- Register a `text/html+skybridge` resource with CSP hints
- Expose a tool with `openai/outputTemplate` and widget metadata
- Return structured content + narration with `build_widget_tool_response`

Install

- pip: `pip install fastmcp-apps-sdk`
- uv: `uv add fastmcp-apps-sdk`

Usage

```
from fastmcp import FastMCP
from fastmcp_apps_sdk import widget, build_widget_tool_response, register_decorated_widgets

@widget(
    identifier="hello-widget",
    title="Hello Widget",
    template_uri="ui://widget/hello.html",
    invoking="Saying hello",
    invoked="Said hello",
    html='<div id="hello-root"></div><script type="module" src="https://example.com/hello.js"></script>',
)
def hello(name: str = "world"):
    return build_widget_tool_response(
        response_text=f"Hello {name}!",
        structured_content={"name": name},
    )

mcp = FastMCP(name="demo", instructions="Demo widgets")
register_decorated_widgets(mcp)
mcp.run(transport="http", host="0.0.0.0", port=8080)
```

Examples

- See `examples/` for Solar System and Pizza widgets.
- Run locally (with uv):
  - `uv pip install -e .` (or `pip install -e .`)
  - `uv run examples/server.py`
  - `ngrok http 8080` and use the HTTPS URL as the MCP endpoint.

Publish to PyPI

- Ensure your version in `pyproject.toml` is updated.
- Build with uv: `uv build` (creates wheel and sdist under `dist/`)
- Publish with uv: `uv publish --token <pypi-token>`
- Alternative with Twine:
  - `python -m pip install build twine`
  - `python -m build`
  - `twine upload dist/*`

Notes

- No auth, env vars, or external tools are included in this package.
- The example server intentionally runs without authentication for easy testing.

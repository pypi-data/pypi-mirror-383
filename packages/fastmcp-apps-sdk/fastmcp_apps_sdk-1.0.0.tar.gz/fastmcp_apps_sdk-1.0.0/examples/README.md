## Examples for fastmcp-apps-sdk

- Solar System and Pizza widgets
- Minimal FastMCP server without auth
- Testable locally and via ngrok

Quickstart

- Install dependencies: `uv pip install -e .` (or `pip install -e .`)
- Run the example server: `uv run examples/server.py`
- Expose with ngrok: `ngrok http 8080`
- Use the HTTPS forwarding URL as your MCP endpoint.

Commands

- Start server: `uv run examples/server.py`
- Start ngrok: `ngrok http 8080`

Notes

- The example server registers the example widgets and serves resources under `ui://widget/...`.
- No auth, env vars, or external tools are required.

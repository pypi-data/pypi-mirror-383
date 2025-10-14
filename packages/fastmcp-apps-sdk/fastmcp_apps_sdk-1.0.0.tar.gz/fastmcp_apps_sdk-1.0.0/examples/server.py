from fastmcp import FastMCP

# Import example widgets so their decorators register into the SDK registry.
from examples.widgets import solar_system  # noqa: F401
from examples.widgets import pizzaz  # noqa: F401

from fastmcp_apps_sdk import register_decorated_widgets


def main() -> None:
    mcp = FastMCP(
        name="fastmcp-apps-sdk-examples",
        instructions="Example widgets (solar system, pizza) using fastmcp-apps-sdk.",
    )

    register_decorated_widgets(mcp)

    # Run without auth on port 8080 for easy local and ngrok testing.
    mcp.run(transport="http", host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()

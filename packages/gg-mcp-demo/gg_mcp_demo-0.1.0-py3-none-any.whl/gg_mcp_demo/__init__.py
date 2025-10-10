from mcp.server.fastmcp import FastMCP

# Create an MCP Server
mcp = FastMCP("sum")

# Add an addtion tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a persnalized greeting"""
    return f"Hello, {name}!"


def main() -> None:
    mcp.run(transport="stdio")

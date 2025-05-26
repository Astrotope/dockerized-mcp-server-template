# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

# Create an MCP server
mcp = FastMCP("StatelessServer", stateless_http=True)


# Add an addition tool
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

# Add a multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
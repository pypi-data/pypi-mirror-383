#server.py
from mcp.server.fastmcp import FastMCP
mcp = FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
@mcp.resource("greeting://{name}")
def greet(name: str) -> str:
    """Greet the user"""
    return f"Hello, {name}"

def main() -> None:
    mcp.run(transport='stdio')

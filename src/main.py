from fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.requests import Request

# Create your FastMCP server as well as any tools, resources, etc.
mcp = FastMCP("MyServer", stateless_http=True)

# Add an addition tool
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

# # Health check route
# async def health_check(request):
#     return JSONResponse({"status": "ok"})

# # Create the ASGI app
# mcp_app = mcp.http_app(path='/mcp')

# # Create a Starlette app and mount the MCP server
# app = Starlette(
#     routes=[
#         Route("/health", health_check),
#         Mount("/mcp", app=mcp_app),
#         # Add other routes as needed
#     ],
#     lifespan=mcp_app.lifespan,
# )

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    mcp.run(transport="streamable-http")

# if __name__ == "__main__":

#     import asyncio
#     asyncio.run(mcp.run_http_async(stateless_http=True))
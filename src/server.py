from fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.requests import Request

import json
from typing import Dict, Optional, Union

from weather import get_weather_summary
from location import get_coordinates

# Create an MCP server
mcp = FastMCP("StatelessServer", 
stateless_http=True,
)

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

@mcp.tool()
async def geocode_place(place_name: str) -> Dict[str, Optional[str]]:
    """
    Get latitude and longitude coordinates for a given place name.
    
    Args:
        place_name: The name of the place to geocode (e.g., "florida", "New York")
    
    Returns:
        A dictionary with 'latitude', 'longitude', and 'status' keys
    """
    return get_coordinates(place_name)

@mcp.tool()
async def get_current_weather(lat: float, lon: float) -> Dict[str, Union[float, str, None]]:
    """
    Get current weather summary (temperature, wind speed, direction) for given coordinates.

    Args:
        lat: Latitude (e.g., 52.52)
        lon: Longitude (e.g., 13.405)

    Returns:
        Dictionary with weather data and status
    """
    return await get_weather_summary(lat, lon)


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


# cli test
# curl -N -X POST http://0.0.0.0:8000/mcp/tools/list -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'

# @contextlib.asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with contextlib.AsyncExitStack() as stack:
#         await stack.enter_async_context(mcp.session_manager.run())
#         yield

# app = FastAPI(lifespan=lifespan)

# app.mount("/mcp", mcp.streamable_http_app())

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

# # Create the ASGI app
# mcp_app = mcp.http_app(path='/mcp')

# # Create a FastAPI app and mount the MCP server
# app = FastAPI(lifespan=mcp_app.lifespan)
# app.mount("/mcp", mcp_app)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})



# test
# curl http://0.0.0.0:8000/health
# curl  GET http://0.0.0.0:8000/heal-N -X POST http://0.0.0.0:8000/mcp/tools/list -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
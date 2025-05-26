from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
import os
from pydantic import BaseModel, Field
from typing import Literal

class WeatherResponse(BaseModel):
    temperature: float = Field(..., description="Temperature in degrees Celsius")
    wind_speed: float = Field(..., description="Wind speed in meters per second")
    wind_direction: Literal[
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ] = Field(..., description="Wind direction as a 16-point compass direction")

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 22.5,
                "wind_speed": 5.3,
                "wind_direction": "NE"
            }
        }


async def test():

    client = MultiServerMCPClient(
        {
            "tools": {
                # Ensure your start your weather server on port 8000
                "url": "https://mcp-server.sliplane.app/mcp",
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()
    agent = create_react_agent(
        "anthropic:claude-3-7-sonnet-latest",
        tools,
        response_format=WeatherResponse
    )

    # weather_response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    # )

    async for chunk in agent.astream(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    stream_mode="updates"
    ):print(chunk)

    response = chunk["generate_structured_response"]["structured_response"]

    print(
    f"Temperature: {response.temperature} °C | "
    f"Wind Speed: {response.wind_speed} m/s | "
    f"Wind Direction: {response.wind_direction}"
    )

if __name__ == "__main__":
    asyncio.run(test())
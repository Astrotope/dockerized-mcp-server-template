from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
import os
import json
from pydantic import BaseModel, Field
from typing import Literal

from mattermostdriver import Driver

mmd = Driver({
    'url': 'mattermost-astrotope.sliplane.app',
    'login_id': 'astrotope',
    'password': 'T3k5Fqs7FaVU9LO',
    'token': 'bbsjobqfwfdzifkcgyudc67imy',
    'scheme': 'https',
    'port': 443,
    'basepath': '/api/v4'
})

mmd.login()

channel_id = mmd.channels.get_channel_by_name_and_team_name('astrotopeorg', 'mcp')['id']

def sent_to_mm(message: str) -> None:
    mmd.posts.create_post(options={
    'channel_id': channel_id,
    'message': message})

channel_id = mmd.channels.get_channel_by_name_and_team_name('astrotopeorg', 'mcp')['id']

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
    ):
        # Convert AIMessage objects to dicts if needed
        def serialize(obj):
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            else:
                return str(obj)

        data = json.loads(json.dumps(chunk, default=serialize, indent=2))

        first_key = list(data.keys())[0]

        if first_key == "agent":
            messages = data["agent"]["messages"]
            content = messages[0]["content"]

            if isinstance(content, list):
                first_content = content[0]
                if isinstance(first_content, dict) and "text" in first_content:
                    print(first_content["text"])
                    sent_to_mm(first_content["text"])
                else:
                    print(first_content)
                    sent_to_mm(first_content)
            elif isinstance(content, str):
                print(content)
                sent_to_mm(content)
            else:
                print(content)
                sent_to_mm(content)

        elif first_key == "tools":
            print(data["tools"]["messages"][0]["content"])
            sent_to_mm(data["tools"]["messages"][0]["content"])

        elif first_key == "generate_structured_response":
            print(data["generate_structured_response"]["structured_response"])
            sent_to_mm(json.dumps(data["generate_structured_response"]["structured_response"]))

    response = chunk["generate_structured_response"]["structured_response"]

    print(
    f"Temperature: {response.temperature} °C | "
    f"Wind Speed: {response.wind_speed} m/s | "
    f"Wind Direction: {response.wind_direction}"
    )

if __name__ == "__main__":
    asyncio.run(test())
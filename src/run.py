import asyncio
from agent_runner import graph

async def main():
    user_input = "What's the weather like in Paris?"
    result = await graph.invoke({"input": user_input})
    print("Response:\n", result)

if __name__ == "__main__":
    asyncio.run(main())

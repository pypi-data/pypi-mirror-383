import asyncio

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP


async def main():
    mcp = MCPServerStreamableHTTP("http://127.0.0.1:8000/mcp/")

    agent = Agent(
        "openai:gpt-4o",
        mcp_servers=[mcp],
        system_prompt=(
            "You are a BACnet expert. Use the available tools to interact with "
            "BACnet devices via the MCP server."
        ),
    )

    async with agent.run_mcp_servers():
        for prompt in [
            "Read the presentValue property of analogInput,1.",
            "Write the value 42 to analogValue instance 1.",
        ]:
            resp = await agent.run(prompt)
            print(resp.output)


if __name__ == "__main__":
    asyncio.run(main())

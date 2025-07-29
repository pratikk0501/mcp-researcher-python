import asyncio
from mcp.server.fastmcp import FastMCP
from agents import research

# Create FastMCP instance
mcp = FastMCP("crew_search")

@mcp.tool()
async def crew_search(query: str) -> str:
    """Run CrewAI-based search system for given user prompt. Does both standard and deep web search.

    Args:
        query (str): The search query or question.

    Returns:
        str: The search response from the CrewAI pipeline.
    """
    return research(query)


# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")


# add this inside ./.cursor/mcp.json
# {
#   "mcpServers": {
#     "crew_search": {
#       "command": "uv",
#       "args": [
#         "--directory",
#         "/Users/kumar/ansel/gen-ai-projects/mcp-deep-researcher",
#         "run",
#         "main.py"
#       ],
#       "env": {
#         "LINKUP_API_KEY": "linkup_api_key"
#       }
#     }
#   }
# }
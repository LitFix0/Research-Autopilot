from tavily import TavilyClient
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from core.config import TAVILY_API_KEY, MAX_SEARCH_RESULTS


# ── Tavily client (shared) ────────────────────────────────
_client = TavilyClient(api_key=TAVILY_API_KEY)


# ── Input schema ──────────────────────────────────────────
class SearchInput(BaseModel):
    query: str = Field(description="The search query to look up on the web.")


# ── Tool definition ───────────────────────────────────────
class TavilySearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Search the web for up-to-date information on a given query. "
        "Returns a list of results with titles, URLs, and content snippets. "
        "Use this whenever you need current facts, news, or research data."
    )
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        try:
            response = _client.search(
                query=query,
                max_results=MAX_SEARCH_RESULTS,
                search_depth="advanced",    # deeper crawl, still free tier
                include_answer=True,        # Tavily's own AI summary on top
            )

            # ── Format output for the agent ───────────────
            lines = []

            if response.get("answer"):
                lines.append(f"Quick answer: {response['answer']}\n")

            for i, result in enumerate(response.get("results", []), 1):
                lines.append(f"[{i}] {result.get('title', 'No title')}")
                lines.append(f"    URL     : {result.get('url', '')}")
                lines.append(f"    Snippet : {result.get('content', '')[:300]}")
                lines.append("")

            return "\n".join(lines) if lines else "No results found."

        except Exception as e:
            return f"Search failed: {str(e)}"


# ── Factory ───────────────────────────────────────────────
def get_search_tool() -> TavilySearchTool:
    """Return a ready-to-use search tool instance."""
    return TavilySearchTool()


if __name__ == "__main__":
    tool = get_search_tool()
    result = tool._run("what is CrewAI multi agent framework")
    print(result)
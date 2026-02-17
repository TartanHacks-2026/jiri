"""NewsAPI MCP Server — stdio transport.

Run directly:  python servers/news_server.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=True)

mcp = FastMCP("news")

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")


@mcp.tool()
def get_news(
    keyword: str,
    category: str = "business",
    language: str = "en",
    country: str = "us",
) -> str:
    """Get news articles about a specific keyword using NewsAPI."""
    try:
        from newsapi import NewsApiClient

        newsapi = NewsApiClient(api_key=NEWS_API_KEY)

        top_headlines = newsapi.get_top_headlines(
            q=keyword,
            category=category,
            language=language,
            country=country,
        )

        if top_headlines["status"] == "ok" and top_headlines["articles"]:
            articles = top_headlines["articles"][:5]
            formatted_news = f"News for '{keyword}':\n\n"

            for i, article in enumerate(articles, 1):
                formatted_news += f"{i}. {article.get('title', 'No title')}\n"
                formatted_news += f"   Source: {article.get('source', {}).get('name', 'Unknown')}\n"
                formatted_news += f"   Published: {article.get('publishedAt', 'Unknown date')}\n"
                formatted_news += f"   URL: {article.get('url', 'No URL')}\n"
                formatted_news += f"   Summary: {article.get('description', 'No description')}\n\n"

            return formatted_news
        else:
            return f"No news articles found for '{keyword}' in the {category} category."

    except Exception as e:
        return f"Error fetching news for '{keyword}': {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

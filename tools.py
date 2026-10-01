import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_query(user_query: str) -> str:
    """
    Search for the topic on the web for the most recent and reliable information.
    Returns the titles, urls and snippets.
    """
    Output_results = []

    search_response = tavily.search(
        query=user_query,
        max_results=4
    )

    results = search_response.get("results", [])

    if not results:
        return "No relevant web results found."

    for result in results:
        title = result.get("title", "No Title")
        url = result.get("url", "")
        content = result.get("content", "")[:400]
        Output_results.append(
            f"Title : {title}\n URL : {url}\n snippet : {content}\n"
        )

    return "\n---\n".join(Output_results)


@tool
def scrape_url(url: str) -> str:
    """
    Scrape and return the clean text content from the given URL for deeper information fetching.
    """
    try:
        response = requests.get(
            url=url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

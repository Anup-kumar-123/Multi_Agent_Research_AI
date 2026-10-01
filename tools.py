from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

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

    # Extract the actual list of results from the response dictionary
    results = search_response.get("results", [])

    for result in results:
        Output_results.append(
            f"Title : {result['title']}\n URL : {result['url']}\n snippet : {result['content'][:400]}\n"
        )

    return "\n---\n".join(Output_results)


@tool
def scrape_url(url : str) -> str:
    """
    Scrape and return the clean text content from the given URL for deeper information fetching.
    """
    try:
        response = requests.get(
            url = url,
            timeout = 8,
            headers = {"User-Agent": "Mozilla/5.0"}
        )
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
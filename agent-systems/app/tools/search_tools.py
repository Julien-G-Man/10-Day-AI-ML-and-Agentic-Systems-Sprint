import os
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

# Main Tavily search tool
web_search = TavilySearchResults(
    max_results=4,
    api_key=os.getenv('TAVILY_API_KEY'),
    name='web_search',
    description=(
        'Search the web for current news, recent events, and up-to-date information. '
        'Use for: latest mission news, recent scientific findings, current status updates. '
        'Do NOT use for basic orbital calculations or static technical specs.'
    ),
)

@tool
def search_satellite_news(satellite_name: str, topic: str = 'latest news') -> str:
    """
    Search specifically for recent news and events related to a satellite mission.
    Use after looking up basic data to find: recent discoveries, status updates,
    mission achievements, anomalies, or upcoming events.
    """
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
    query  = f'{satellite_name} {topic} 2024 2025'
    results = client.search(query, max_results=3, search_depth='advanced')
    if not results.get('results'):
        return f'No news found for {satellite_name}'
    formatted = []
    for r in results['results']:
        formatted.append(f"Source: {r['url']}\nTitle: {r['title']}\nSummary: {r['content'][:300]}\n")
    return '\n'.join(formatted)

import time
import requests

# API endpoints and constants
QUERY_URL = "https://app.runathena.com/api/v2/query-async"
RESULTS_URL = "https://app.runathena.com/api/v2/get-results"
HEADERS = {"Content-Type": "application/json"}
ARTICLES_PER_PAGE = 25

def send_initial_query(query: str, key_phrases: str, api_key: str, toggle_state: str, start_date: str, end_date: str) -> str:
    """
    Sends the initial query to the API and returns the query_id.
    """
    payload = {
        "query": query,
        "key_phrases": key_phrases,
        "api_key": api_key,
        "toggle_state": toggle_state,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(QUERY_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get('query_id')

def poll_for_results(query_id: str, api_key: str, poll_interval: int = 1) -> dict:
    """
    Polls the API until the query state changes from 'PENDING'.
    Returns the final result data.
    """
    payload = {"query_id": query_id, "api_key": api_key}
    response = requests.post(RESULTS_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()

    while data.get('state') == 'PENDING':
        time.sleep(poll_interval)
        response = requests.post(RESULTS_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
    return data

def fetch_all_articles(query_id: str, total_results: int, api_key: str, toggle_state: str = 'All Articles') -> list:
    """
    Fetches and aggregates all articles by paginating through the results.
    """
    all_articles = []
    page = 1
    payload = {"query_id": query_id, "api_key": api_key, "toggle_state": toggle_state}

    while (page - 1) * ARTICLES_PER_PAGE < total_results:
        payload['page'] = page
        response = requests.post(RESULTS_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        all_articles.extend(articles)
        page += 1
    return all_articles

def news(start_date: str, end_date: str, query: str, key_phrases: Optional[str] = None, toggle_state: str = "All Articles", api_key: str, poll_interval: int = 1) -> list:
    """
    Queries the Athena News API and returns a list of articles.

    Parameters:
      - start_date (str): ISO formatted start date.
      - end_date (str): ISO formatted end date.
      - query (str): The search query.
      - key_phrases (str): Key phrases to refine the search.
      - toggle_state (str): The toggle state (e.g., "All Articles").
      - api_key (str): Your Athena API key.
      - poll_interval (int, optional): Seconds to wait between polls (default is 1).

    Returns:
      - list: A list of articles returned by the API.
    """
    query_id = send_initial_query(query, key_phrases, api_key, toggle_state, start_date, end_date)
    if not query_id:
        raise ValueError("Failed to retrieve query ID.")

    result_data = poll_for_results(query_id, api_key, poll_interval)
    if result_data.get('state') != 'SUCCESS':
        raise RuntimeError(f"Query did not complete successfully: {result_data}")

    total_results = result_data.get('totalArticles', 0)
    if total_results == 0:
        return []

    all_articles = fetch_all_articles(query_id, total_results, api_key)
    return all_articles

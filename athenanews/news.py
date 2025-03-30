import time
import requests
from typing import Optional
import datetime


# API endpoints and constants
QUERY_URL = "https://app.runathena.com/api/v2/query-async"
RESULTS_URL = "https://app.runathena.com/api/v2/get-results"
HEADERS = {"Content-Type": "application/json"}
ARTICLES_PER_PAGE = 25

def parse_date_to_datetime(date_str: str) -> datetime.datetime:
    """
    Parses a date string into a datetime object. Supports full ISO strings
    (with time) or the simpler 'YYYY-MM-DD' format. Assumes UTC.
    """
    try:
        # Try to parse as full ISO format (strip trailing 'Z' if present)
        dt = datetime.datetime.fromisoformat(date_str.rstrip("Z"))
    except ValueError:
        # Fallback to date-only format
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    # Assume UTC if no timezone info is present
    return dt.replace(tzinfo=datetime.timezone.utc)

def datetime_to_isodate(dt: datetime.datetime) -> str:
    """
    Converts a datetime object to an ISO-formatted string that includes microseconds,
    in the format '%Y-%m-%dT%H:%M:%S.%fZ'.
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def send_initial_query(query: str, key_phrases: str, api_key: str, toggle_state: str, start_date: str, end_date: str) -> str:
    """
    Sends the initial query to the API and returns the query_id.
    """
    try:
        print('hi')
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
        if data['state'] == 'SUCCESS':
            return data.get('query_id')
        else:
            print(data)
            return data
    except Exception as e:
        print(str(e))

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

def _search_chunk(start_date: str, end_date: str, query: str, key_phrases: str, toggle_state: str, api_key: str, poll_interval: int = 1) -> list:
    """
    Helper function that performs the search for a given date range chunk.
    """
    query_id = send_initial_query(query, key_phrases, api_key, toggle_state, start_date, end_date)
    
    if isinstance(query_id, str) == False:
        if query_id.get('message'):
            raise Exception(str(query_id['message']))

    if not query_id:
        raise Exception("Failed to retrieve query ID.")

    result_data = poll_for_results(query_id, api_key, poll_interval)
    if result_data.get('state') != 'SUCCESS':
        raise RuntimeError(f"Query did not complete successfully: {result_data}")

    total_results = result_data.get('totalArticles', 0)
    if total_results == 0:
        return []

    articles = fetch_all_articles(query_id, total_results, api_key)
    return articles

def news(
    start_date: str,
    end_date: str,
    query: str,
    api_key: str,
    key_phrases: Optional[str] = None,
    threshold: Optional[float] = .00055,
    toggle_state: str = "All Articles",
    poll_interval: int = 1
) -> list:
    """
    Queries the Athena News API and returns a list of articles.
    
    If the date range between start_date and end_date exceeds 7 days, the search
    is divided into 7-day chunks. The results from all chunks are then combined
    and sorted by article score (descending).
    
    This function accepts dates in various formats (full ISO or 'YYYY-MM-DD') and
    converts them to ISO format (which MongoDB accepts).
    
    Parameters:
      - start_date (str): Start date in ISO format or 'YYYY-MM-DD'.
      - end_date (str): End date in ISO format or 'YYYY-MM-DD'.
      - query (str): The search query.
      - api_key (str): Your Athena API key.
      - key_phrases (Optional[str]): Additional key phrases. Defaults to None.
      - toggle_state (str): The toggle state. Defaults to "All Articles".
      - poll_interval (int): Seconds to wait between polls (default is 1).
    
    Returns:
      - list: Combined and sorted list of articles.
    """
    if key_phrases is None:
        key_phrases = ""

    # Parse input dates into datetime objects and then convert to ISO format
    start_dt = parse_date_to_datetime(start_date)
    end_dt = parse_date_to_datetime(end_date)
    
    start_iso = datetime_to_isodate(start_dt)
    end_iso = datetime_to_isodate(end_dt)
    
    delta_days = (end_dt - start_dt).days
    all_articles = []

    if delta_days > 7:
        current_start = start_dt
        while current_start < end_dt:
            current_end = current_start + datetime.timedelta(days=7)
            if current_end > end_dt:
                current_end = end_dt
            # Convert each chunk's datetime to ISO format for the API call
            chunk_start = datetime_to_isodate(current_start)
            chunk_end = datetime_to_isodate(current_end)
            articles = _search_chunk(chunk_start, chunk_end, query, key_phrases, toggle_state, api_key, poll_interval)
            all_articles.extend(articles)
            current_start = current_end
        # Sort articles by 'score' in descending order (assumes each article dict has a 'score' key)
        all_articles.sort(key=lambda a: a.get("score", 0), reverse=True)
    else:
        all_articles = _search_chunk(start_iso, end_iso, query, key_phrases, toggle_state, api_key, poll_interval)

    all_articles = [item for item in all_articles if item.get("score", 0) > 0.00055]

    return all_articles
# Athena News API Wrapper

A simple Python wrapper for the [Athena News API](https://runathena.com) that simplifies querying and retrieving news articles.

## Features

- **Simplified API Access:** Easily send queries to the Athena News API.
- **Automatic Polling:** Automatically polls until the query is processed.
- **Pagination Handling:** Fetches all available articles across multiple pages.

## Installation

Install the package via pip (after publishing to PyPI):

`pip install athenanewsapi`

Or install directly from source:

```
git clone https://github.com/athenanewsapi/athenanews.git
cd athenanewsapi
pip install .
```
Then get your API key by [creating an Athena account](https://app.runathena.com/register). 

## Usage

Import the package and call the news function with the required parameters:

```
from athenanewsapi import news

articles = news(
    start_date="2025-03-01T15:13:52.466Z",
    end_date="2025-03-20T15:13:52.466Z",
    query="Tesla dealership protests",
    key_phrases="('tesla takedown')",
    toggle_state="All Articles",
    api_key="YOUR_API_KEY"
)

print("Total articles fetched:", len(articles))
```

## API Reference

news(start_date, end_date, query, key_phrases, toggle_state, api_key)

- **start_date (str):** ISO formatted start date.
- **end_date (str):** ISO formatted end date.
- **query (str):** The search query.
- **key_phrases (str) OPTIONAL:** Key phrases to refine the search. (ex: `('elon' or 'musk') and not 'sam altman'`)
- **toggle_state (str) OPTIONAL:** The toggle state (e.g., "All Articles" or "Encoded Articles").
- **api_key (str):** Your Athena API key.

**Returns:**
A list of articles returned by the API.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.


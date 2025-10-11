# BDClient

An unofficial type-safe Python client for Bright Data APIs.

Features:
- Scraper API
    - Google News
    - Google SERP
    - YouTube Videos
- Unlocker API

## Installation

Installing using pip:
```
pip install bdclient
```

Installing using uv:
```
uv add bdclient
```

## Usage

Example scraper usage:
```python
import asyncio

from bdclient.scraper.youtube_videos import DiscoverByKeyword, DiscoverByKeywordQuery


async def main():
    scraper = DiscoverByKeyword(api_key="your_bright_data_api_key")
    query = DiscoverByKeywordQuery(keyword="Latest News")

    results = await scraper.scrape([query])
    for result in results:
        print(result.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
```

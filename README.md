# Iranian Car Data Crawler (Divar)

A Python crawler for extracting car listings from Divar.ir, Iran's largest classifieds platform. The tool uses Divar's internal API, implements recursive post extraction to handle structural changes, and exports data to CSV.

## Why Divar?

Divar.ir is the most visited classifieds website in Iran, offering millions of active listings. For vehicle market analysis, Divar provides:
- High volume of car ads (new and used).
- City-level filtering, essential for regional price studies.
- A semi-public API used by the web frontend, allowing efficient data collection.
- No mandatory authentication for read-only search endpoints (as of now).

Compared to other Iranian car platforms (Bama, IranCar), Divar has broader coverage and more frequent updates.

## Why This Crawling Method?

Three approaches were considered:
1. HTML parsing (BeautifulSoup) – slow, brittle, requires JavaScript rendering.
2. Browser automation (Selenium) – resource-heavy, easily blocked.
3. Direct API interaction – fast, lightweight, and mimics the official client.

API-based scraping was chosen because:
- Speed: JSON responses are returned in milliseconds.
- Lower server load: one request per page versus dozens for HTML.
- Stability: API structures change less often than HTML layouts.
- Maintainability: a recursive key search adapts to nesting changes.

The crawler replicates Divar's web requests (headers, payload format, pagination tokens) to appear as a legitimate browser session.

## Technical Approach

- **Endpoint:** `POST https://api.divar.ir/v8/web-search/{city}/car`
- **Payload:** `{"json_schema": {"category": {"value": "car"}}}`
- **Pagination:** uses `last_post_date` from response, sent as `last-post-date` in next request.
- **Recursive extraction:** instead of a fixed path (`widget_list[0].data.posts`), the crawler recursively searches for any dictionary key named `"posts"` that contains a non-empty list. This makes it resilient to API changes. If Divar renames the key to `"listings"` or `"ads"`, the function can be easily extended.

## Installation

Requires Python 3.7+ and two libraries:

```bash
pip install requests pandas
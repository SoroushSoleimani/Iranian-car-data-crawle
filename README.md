# Iranian Car Data Crawler (Divar)

A Python crawler to collect car listings from [Divar.ir](https://divar.ir), Iran's leading classified ads platform. The script fetches car ads from a given city (e.g., Tehran, Karaj, Mashhad) and saves them as a CSV file.

> **Note:** Divar’s API structure may change over time. The current version implements a recursive search for ad posts, making it more resilient to structural changes.

## Features

- Fetch car ads from any supported city
- Pagination support (auto‑loads next pages)
- Extracts: title, subtitle, price, ad token, URL, city, and scrape timestamp
- Saves data to UTF‑8 encoded CSV
- Adjustable delay between requests to avoid rate limiting

## Requirements

- Python 3.7+
- `requests`
- `pandas`

## Installation

1. Clone or download this repository.
2. Install dependencies:

```bash
pip install requests pandas
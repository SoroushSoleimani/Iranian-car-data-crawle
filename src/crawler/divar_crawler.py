import time
import os
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any

class DivarCarCrawler:
    BASE_URL = "https://api.divar.ir/v8/web-search"

    def __init__(self, city: str = "tehran", delay: float = 1.0):
        self.city = city
        self.delay = delay
        self.data: List[Dict[str, Any]] = []

    def _fetch_page(self, last_post_token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{self.city}/car"
        payload: Dict[str, Any] = {"json_schema": {"category": {"value": "car"}}}
        if last_post_token:
            payload["last-post-date"] = last_post_token

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://divar.ir/",
            "Accept": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _find_posts(self, obj):
        """Recursively find any key named 'posts' that contains a list."""
        if isinstance(obj, dict):
            if "posts" in obj and isinstance(obj["posts"], list) and obj["posts"]:
                return obj["posts"]
            for value in obj.values():
                res = self._find_posts(value)
                if res:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = self._find_posts(item)
                if res:
                    return res
        return []

    def scrape(self, limit: int = 50) -> List[Dict[str, Any]]:
        print(f"[INFO] Start scraping up to {limit} car ads from city='{self.city}'")
        self.data = []
        last_post_token = None
        empty_count = 0

        while len(self.data) < limit:
            json_data = self._fetch_page(last_post_token)
            posts = self._find_posts(json_data)

            if not posts:
                empty_count += 1
                print(f"[WARN] No posts found (attempt {empty_count})")
                if empty_count >= 2:
                    break
                last_post_token = json_data.get("last_post_date")
                if not last_post_token:
                    break
                time.sleep(self.delay)
                continue

            empty_count = 0
            for post in posts:
                if len(self.data) >= limit:
                    break

                token = post.get("token") or post.get("data", {}).get("token")
                if not token:
                    continue

                title = post.get("title") or post.get("data", {}).get("title") or ""
                subtitle = post.get("subtitle") or post.get("data", {}).get("subtitle") or ""
                details = post.get("data", {}).get("middle_description_text") or post.get("description", "")

                # Price extraction
                price = None
                if "price" in post:
                    p = post["price"]
                    if isinstance(p, dict):
                        price = p.get("text") or p.get("display")
                    elif isinstance(p, str):
                        price = p
                if not price and "data" in post and isinstance(post["data"], dict):
                    data = post["data"]
                    if "price" in data:
                        p = data["price"]
                        if isinstance(p, dict):
                            price = p.get("text") or p.get("display")
                        elif isinstance(p, str):
                            price = p
                    if not price and "badge" in data:
                        for badge in data["badge"]:
                            if badge.get("type") == "PRICE":
                                price = badge.get("text")
                                break
                if not price and "badge" in post:
                    for badge in post["badge"]:
                        if badge.get("type") == "PRICE":
                            price = badge.get("text")
                            break

                self.data.append({
                    "token": token,
                    "url": f"https://divar.ir/v/{token}",
                    "title": title,
                    "subtitle": subtitle,
                    "details": details,
                    "price": price,
                    "city": self.city,
                    "scraped_at": datetime.now().isoformat(timespec="seconds"),
                })

            last_post_token = json_data.get("last_post_date")
            if not last_post_token:
                print("[INFO] No more pages (last_post_date missing)")
                break

            print(f"[INFO] Collected {len(self.data)} ads so far...")
            time.sleep(self.delay)

        print(f"[INFO] Scraping finished. Total: {len(self.data)}")
        return self.data

    def save_csv(self, filename: Optional[str] = None) -> None:
        if not self.data:
            print("[WARN] No data to save")
            return
        if filename is None:
            os.makedirs("data", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/cars_divar_{self.city}_{timestamp}.csv"
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"[INFO] Saved {len(df)} rows to {filename}")


if __name__ == "__main__":
    crawler = DivarCarCrawler(city="tehran", delay=1.0)
    try:
        crawler.scrape(limit=50)
        crawler.save_csv()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted. Saving partial data...")
        crawler.save_csv()
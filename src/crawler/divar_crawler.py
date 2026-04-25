 
import requests
import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

class DivarCrawler:
    def __init__(self):
        self.data = []
        self.base_url = "https://divar.ir"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def search_cars(self, city="tehran", limit=20):
        url = f"{self.base_url}/s/{city}/car"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        post_links = []
        for a in soup.find_all('a', href=True):
            if '/v/' in a['href'] and a['href'] not in post_links:
                post_links.append(a['href'])

        post_links = list(dict.fromkeys(post_links))[:limit]

        for idx, link in enumerate(post_links, 1):
            post_data = self.get_post_details(link)
            if post_data:
                self.data.append(post_data)
            time.sleep(1)

        return self.data

    def get_post_details(self, post_link):
        full_url = self.base_url + post_link if post_link.startswith('/') else post_link
        try:
            response = requests.get(full_url, headers=self.headers)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            title_tag = soup.find('h1')
            title = title_tag.text.strip() if title_tag else "بدون عنوان"

            price_tag = soup.find('div', class_='kt-post-price__value')
            price = price_tag.text.strip() if price_tag else "قیمت درج نشده"

            desc_tag = soup.find('div', class_='kt-description-row__text')
            description = desc_tag.text.strip() if desc_tag else ""

            location_tag = soup.find('div', class_='kt-page-title__subtitle--responsive')
            location = location_tag.text.strip() if location_tag else "نامشخص"

            return {
                'url': full_url,
                'title': title,
                'price': price,
                'description': description[:200],
                'location': location,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception:
            return None

    def save_to_csv(self, filename=None):
        if not self.data:
            return None

        if filename is None:
            filename = f"data/cars_divar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        import os
        os.makedirs('data', exist_ok=True)

        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename

def run():
    crawler = DivarCrawler()
    crawler.search_cars(city="tehran", limit=10)
    crawler.save_to_csv()

if __name__ == "__main__":
    run()
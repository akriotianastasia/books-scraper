import os
from typing import List, Dict, Optional
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

BASE_URL = "https://books.toscrape.com/"
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"


def rating_to_int(rating_word: str) -> int:
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return mapping.get(rating_word, 0)


def scrape_books(max_pages: int = 1) -> List[Dict]:
    """
    Scrape βιβλία από το Books to Scrape για max_pages σελίδες (1 = μόνο η πρώτη).
    """
    books: List[Dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            slow_mo=50 if not HEADLESS else 0,
        )
        page = browser.new_page()

        page.goto(BASE_URL, wait_until="domcontentloaded")
        pages_scraped = 0

        while pages_scraped < max_pages:
            pages_scraped += 1

            articles = page.locator("article.product_pod")
            for i in range(articles.count()):
                book = articles.nth(i)
                try:
                    title = book.locator("h3 a").get_attribute("title") or ""
                    rel_url = book.locator("h3 a").get_attribute("href") or ""
                    url = BASE_URL + rel_url.replace("../", "")

                    price_text = book.locator(".price_color").inner_text()
                    price = float(price_text.replace("£", "").strip())

                    availability = book.locator(".availability").inner_text().strip()

                    cls = book.locator("p.star-rating").get_attribute("class") or ""
                    rating_word = cls.split()[-1] if cls else ""
                    rating = rating_to_int(rating_word)

                    books.append(
                        {
                            "title": title,
                            "price": price,
                            "availability": availability,
                            "rating": rating,
                            "url": url,
                            "page": pages_scraped,
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Skipped book at index {i} on page {pages_scraped}: {e}")

            # Βρες το "Next" (αν δεν υπάρχει, τέλος)
            next_link = page.locator("li.next a")
            if next_link.count() == 0:
                break

            next_href = next_link.first.get_attribute("href")
            if not next_href:
                break

            next_url = urljoin(page.url, next_href)
            page.goto(next_url, wait_until="domcontentloaded")

        browser.close()

    return books

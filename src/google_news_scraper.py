import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define project root and output directory using absolute paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

async def scrape_google_news(keyword, max_articles=50, stop_event=None):
    """
    Scrapes news articles from Google News based on a keyword.

    Args:
        keyword (str): The search term.
        max_articles (int): The maximum number of articles to scrape.
        stop_event (threading.Event, optional): An event to signal stopping.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped news articles.
    """
    logging.info(f"Starting Google News scraping for keyword: '{keyword}'")

    all_articles = []
    article_urls = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # 1. Navigate to Google News and perform search
            search_url = f"https://news.google.com/search?q={keyword.replace(' ', '%20')}&hl=id&gl=ID&ceid=ID:id"
            logging.info(f"Navigating to {search_url}")
            await page.goto(search_url, wait_until="domcontentloaded")

            # 2. Scroll to load more articles
            logging.info(f"Scrolling to load up to {max_articles} articles...")
            last_height = 0
            while len(all_articles) < max_articles:
                if stop_event and stop_event.is_set():
                    logging.info("Stop event received. Halting scraping.")
                    break

                # Scroll down
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2) # Wait for content to load

                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    logging.info("Reached the end of the page.")
                    break
                last_height = new_height

                # 3. Scrape articles on the page
                articles = await page.query_selector_all("article")
                for article in articles:
                    if len(all_articles) >= max_articles:
                        break

                    try:
                        link_element = await article.query_selector("a")
                        if not link_element: continue

                        relative_url = await link_element.get_attribute("href")
                        # URLs are relative, so we need to resolve them
                        full_url = f"https://news.google.com{relative_url[1:]}"

                        if full_url in article_urls:
                            continue

                        title_element = await article.query_selector("h3")
                        title = await title_element.inner_text() if title_element else "No Title"

                        source_element = await article.query_selector("div[data-n-tid]")
                        source = await source_element.inner_text() if source_element else "No Source"

                        time_element = await article.query_selector("time")
                        published_time = await time_element.get_attribute("datetime") if time_element else "No Time"

                        # Snippet is harder, it's usually after the main link in the same container
                        snippet_element = await article.query_selector("span.xBbh9")
                        snippet = await snippet_element.inner_text() if snippet_element else ""

                        all_articles.append({
                            "Title": title,
                            "Source": source,
                            "Published Time": published_time,
                            "Snippet": snippet,
                            "URL": full_url
                        })
                        article_urls.add(full_url)

                    except Exception as e:
                        logging.warning(f"Could not parse an article, skipping. Error: {e}")

        except Exception as e:
            logging.error(f"An error occurred during Google News scraping: {e}")
            screenshot_path = OUTPUT_DIR / "google_news_error_screenshot.png"
            await page.screenshot(path=screenshot_path)
            logging.info(f"An error screenshot has been saved as '{screenshot_path}'.")

        finally:
            await browser.close()
            logging.info("Browser closed.")

    if not all_articles:
        return pd.DataFrame()

    return pd.DataFrame(all_articles)

if __name__ == '__main__':
    async def main():
        print("Testing Google News Scraper...")
        df = await scrape_google_news("IKN", max_articles=10)

        if not df.empty:
            print("\n--- Google News Scrape Successful ---")
            print(f"Found {len(df)} articles.")
            print(df.head())
            df.to_csv(OUTPUT_DIR / "google_news_test.csv", index=False)
            print(f"Saved to {OUTPUT_DIR / 'google_news_test.csv'}")
        else:
            print("\n--- Google News Scrape Failed ---")

    asyncio.run(main())
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
import re
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define project root and output directory using absolute paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def scrape_x(keyword, start_date, end_date, username, password, max_tweets=100, stop_event=None):
    """
    Main function to scrape data from X (Twitter) using Playwright.
    ...
    """
    logging.info("Starting X/Twitter scraping process.")

    scraped_data = []
    tweet_ids = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. Login to X/Twitter
            logging.info("Navigating to X/Twitter login page.")
            await page.goto("https://twitter.com/login")

            logging.info(f"Logging in as {username}...")
            username_input = page.locator('input[name="text"]')
            await username_input.wait_for(timeout=30000)
            await username_input.fill(username)

            next_button = page.get_by_role("button", name="Next")
            await next_button.click()

            password_input = page.locator('input[name="password"]')
            await password_input.wait_for(timeout=30000)
            await password_input.fill(password)

            login_button = page.get_by_role("button", name="Log in")
            await login_button.click()

            await page.wait_for_url("https://twitter.com/home", timeout=60000)
            logging.info("Login successful.")

            # Add a short delay to mimic human behavior before searching
            logging.info("Pausing for 3 seconds to mimic human behavior...")
            await asyncio.sleep(3)

            # 2. Perform search
            search_query = f"{keyword} since:{start_date} until:{end_date}"
            logging.info(f"Performing search with query: '{search_query}'")

            search_url = f"https://twitter.com/search?q={search_query.replace(' ', '%20')}&src=typed_query&f=live"
            await page.goto(search_url)

            # Add a smart wait to ensure the search results page is ready
            logging.info("Waiting for search results to load...")
            # This selector targets the main timeline container for search results
            await page.wait_for_selector('section[role="region"]', timeout=30000)
            logging.info("Search results page is ready.")

            # 3. Scroll and scrape data
            logging.info(f"Starting to scroll and scrape a maximum of {max_tweets} tweets...")

            last_height = await page.evaluate("document.body.scrollHeight")

            while len(scraped_data) < max_tweets:
                if stop_event and stop_event.is_set():
                    logging.info("Stop event received. Halting scraping.")
                    break

                await page.wait_for_selector('article[data-testid="tweet"]', timeout=30000)
                tweets = await page.query_selector_all('article[data-testid="tweet"]')

                for tweet in tweets:
                    status_url_element = await tweet.query_selector('a[href*="/status/"]')
                    if not status_url_element: continue

                    status_url = await status_url_element.get_attribute('href')
                    tweet_id_match = re.search(r'/status/(\d+)', status_url)
                    if not tweet_id_match: continue

                    tweet_id = tweet_id_match.group(1)
                    if tweet_id in tweet_ids: continue

                    try:
                        user_info_element = await tweet.query_selector('div[data-testid="User-Name"]')
                        username_text = await user_info_element.inner_text()
                        user_handle = next((part for part in username_text.split('\n') if part.startswith('@')), 'N/A')

                        tweet_text_element = await tweet.query_selector('div[data-testid="tweetText"]')
                        tweet_text = await tweet_text_element.inner_text() if tweet_text_element else ""

                        timestamp_element = await tweet.query_selector('time')
                        timestamp = await timestamp_element.get_attribute('datetime') if timestamp_element else ""

                        reply_count_element = await tweet.query_selector('button[data-testid="reply"]')
                        reply_label = await reply_count_element.get_attribute('aria-label') if reply_count_element else "0"

                        retweet_count_element = await tweet.query_selector('button[data-testid="retweet"]')
                        retweet_label = await retweet_count_element.get_attribute('aria-label') if retweet_count_element else "0"

                        like_count_element = await tweet.query_selector('button[data-testid="like"]')
                        like_label = await like_count_element.get_attribute('aria-label') if like_count_element else "0"

                        like_count = re.search(r'(\d+)', like_label).group(1) if re.search(r'(\d+)', like_label) else "0"
                        retweet_count = re.search(r'(\d+)', retweet_label).group(1) if re.search(r'(\d+)', retweet_label) else "0"
                        reply_count = re.search(r'(\d+)', reply_label).group(1) if re.search(r'(\d+)', reply_label) else "0"

                        scraped_data.append({
                            'Tweet ID': tweet_id, 'Teks Tweet': tweet_text, 'Waktu Posting': timestamp,
                            'Username': user_handle, 'User ID': user_handle.replace('@', ''),
                            'Jumlah Like': int(like_count), 'Jumlah Balasan': int(reply_count),
                            'Jumlah Retweet': int(retweet_count), 'URL Tweet': f"https://twitter.com{status_url}"
                        })
                        tweet_ids.add(tweet_id)

                        if len(scraped_data) >= max_tweets: break
                    except Exception as e:
                        logging.warning(f"Could not parse a tweet, skipping. Error: {e}")

                if len(scraped_data) >= max_tweets: break

                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)

                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    logging.info("Reached the end of the page or no more tweets to load.")
                    break
                last_height = new_height

            logging.info(f"Scraping finished. Found {len(scraped_data)} unique tweets.")

        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
            screenshot_path = OUTPUT_DIR / "error_screenshot.png"
            await page.screenshot(path=screenshot_path)
            logging.info(f"An error screenshot has been saved as '{screenshot_path}'.")

        finally:
            await browser.close()
            logging.info("Browser closed.")

    if not scraped_data:
        columns = ['Tweet ID', 'Teks Tweet', 'Waktu Posting', 'Username', 'User ID', 'Jumlah Like', 'Jumlah Balasan', 'Jumlah Retweet', 'URL Tweet']
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(scraped_data)

if __name__ == '__main__':
    async def main():
        DUMMY_USER = os.environ.get("X_USERNAME", "your_username")
        DUMMY_PASS = os.environ.get("X_PASSWORD", "your_password")

        if DUMMY_USER == "your_username":
            print("Please set X_USERNAME and X_PASSWORD environment variables to test.")
            return

        df = await scrape_x(
            keyword="indonesia", start_date="2024-05-01", end_date="2024-05-02",
            username=DUMMY_USER, password=DUMMY_PASS, max_tweets=20
        )

        if not df.empty:
            print("Scraping successful. Data head:")
            print(df.head())
            csv_path = OUTPUT_DIR / "scraped_tweets.csv"
            df.to_csv(csv_path, index=False)
            print(f"Data saved to {csv_path}")
        else:
            print("Scraping finished with no data.")

    # To run the async main function:
    # asyncio.run(main())
    print("Scraper module updated. Set environment variables and uncomment asyncio.run(main()) to test.")
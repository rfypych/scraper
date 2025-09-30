import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
import re
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def scrape_x(keyword, start_date, end_date, username, password, max_tweets=100, stop_event=None):
    """
    Main function to scrape data from X (Twitter) using Playwright.

    Args:
        keyword (str): The search term to look for.
        start_date (str): The start date for the search (YYYY-MM-DD).
        end_date (str): The end date for the search (YYYY-MM-DD).
        username (str): The X/Twitter username for login.
        password (str): The X/Twitter password for login.
        max_tweets (int): The maximum number of tweets to scrape.
        stop_event (threading.Event, optional): An event to signal stopping the process.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the scraped data.
    """
    logging.info("Starting X/Twitter scraping process.")

    scraped_data = []
    tweet_ids = set()  # To avoid duplicates

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. Login to X/Twitter
            logging.info("Navigating to X/Twitter login page.")
            await page.goto("https://twitter.com/login")

            logging.info(f"Logging in as {username}...")
            # Using more resilient selectors for login
            await page.get_by_label("Phone, email, or username").fill(username)
            await page.get_by_role("button", name="Next").click()

            await page.get_by_label("Password").fill(password)
            await page.get_by_role("button", name="Log in").click()

            await page.wait_for_url("https://twitter.com/home", timeout=60000)
            logging.info("Login successful.")

            # 2. Perform search
            search_query = f"{keyword} since:{start_date} until:{end_date}"
            logging.info(f"Performing search with query: '{search_query}'")

            search_url = f"https://twitter.com/search?q={search_query.replace(' ', '%20')}&src=typed_query&f=live"
            await page.goto(search_url)

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
                    if not status_url_element:
                        continue

                    status_url = await status_url_element.get_attribute('href')
                    tweet_id_match = re.search(r'/status/(\d+)', status_url)
                    if not tweet_id_match:
                        continue

                    tweet_id = tweet_id_match.group(1)
                    if tweet_id in tweet_ids:
                        continue

                    try:
                        user_info_element = await tweet.query_selector('div[data-testid="User-Name"]')
                        username_text = await user_info_element.inner_text()
                        user_handle = next((part for part in username_text.split('\n') if part.startswith('@')), 'N/A')

                        tweet_text_element = await tweet.query_selector('div[data-testid="tweetText"]')
                        tweet_text = await tweet_text_element.inner_text() if tweet_text_element else ""

                        timestamp_element = await tweet.query_selector('time')
                        timestamp = await timestamp_element.get_attribute('datetime') if timestamp_element else ""

                        # Interaction counts are inside an aria-label
                        reply_count_element = await tweet.query_selector('button[data-testid="reply"]')
                        reply_label = await reply_count_element.get_attribute('aria-label') if reply_count_element else "0"

                        retweet_count_element = await tweet.query_selector('button[data-testid="retweet"]')
                        retweet_label = await retweet_count_element.get_attribute('aria-label') if retweet_count_element else "0"

                        like_count_element = await tweet.query_selector('button[data-testid="like"]')
                        like_label = await like_count_element.get_attribute('aria-label') if like_count_element else "0"

                        # Extract numbers from labels
                        like_count = re.search(r'(\d+)', like_label).group(1) if re.search(r'(\d+)', like_label) else "0"
                        retweet_count = re.search(r'(\d+)', retweet_label).group(1) if re.search(r'(\d+)', retweet_label) else "0"
                        reply_count = re.search(r'(\d+)', reply_label).group(1) if re.search(r'(\d+)', reply_label) else "0"

                        scraped_data.append({
                            'Tweet ID': tweet_id,
                            'Teks Tweet': tweet_text,
                            'Waktu Posting': timestamp,
                            'Username': user_handle,
                            'User ID': user_handle.replace('@', ''),
                            'Jumlah Like': int(like_count),
                            'Jumlah Balasan': int(reply_count),
                            'Jumlah Retweet': int(retweet_count),
                            'URL Tweet': f"https://twitter.com{status_url}"
                        })
                        tweet_ids.add(tweet_id)

                        if len(scraped_data) >= max_tweets:
                            break
                    except Exception as e:
                        logging.warning(f"Could not parse a tweet, skipping. Error: {e}")

                if len(scraped_data) >= max_tweets:
                    break

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
            os.makedirs("output", exist_ok=True)
            await page.screenshot(path="output/error_screenshot.png")
            logging.info("An error screenshot has been saved as 'output/error_screenshot.png'.")

        finally:
            await browser.close()
            logging.info("Browser closed.")

    if not scraped_data:
        columns = ['Tweet ID', 'Teks Tweet', 'Waktu Posting', 'Username', 'User ID', 'Jumlah Like', 'Jumlah Balasan', 'Jumlah Retweet', 'URL Tweet']
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(scraped_data)

if __name__ == '__main__':
    async def main():
        # This is a dummy example and will not run without a real login.
        # It demonstrates how the function would be called.
        DUMMY_USER = os.environ.get("X_USERNAME", "your_username")
        DUMMY_PASS = os.environ.get("X_PASSWORD", "your_password")

        if DUMMY_USER == "your_username":
            print("Please set X_USERNAME and X_PASSWORD environment variables to test.")
            return

        stop_event = asyncio.Event()
        df = await scrape_x(
            keyword="indonesia",
            start_date="2024-05-01",
            end_date="2024-05-02",
            username=DUMMY_USER,
            password=DUMMY_PASS,
            max_tweets=20,
            stop_event=stop_event
        )

        if not df.empty:
            print("Scraping successful. Data head:")
            print(df.head())
            df.to_csv("output/scraped_tweets.csv", index=False)
            print("Data saved to output/scraped_tweets.csv")
        else:
            print("Scraping finished with no data.")

    # To run the async main function:
    # asyncio.run(main())
    print("Scraper module updated. Set environment variables and uncomment asyncio.run(main()) to test.")
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

async def scrape_reddit(target, target_type="subreddit", max_posts=25, stop_event=None):
    """
    Scrapes data from Reddit based on a subreddit or search query.

    Args:
        target (str): The name of the subreddit or the search keyword.
        target_type (str): Either "subreddit" or "search".
        max_posts (int): The maximum number of posts to scrape.
        stop_event (threading.Event, optional): An event to signal stopping.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped data (posts and comments).
    """
    logging.info(f"Starting Reddit scraping for {target_type}: '{target}'")

    all_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:
            # 1. Determine the target URL
            if target_type == "Subreddit":
                url = f"https://old.reddit.com/r/{target}/"
            else: # Search
                url = f"https://old.reddit.com/search/?q={target.replace(' ', '+')}"

            logging.info(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded")

            # 2. Scrape the list of posts
            logging.info(f"Scraping up to {max_posts} posts...")
            post_links = []

            # The selector for post entries
            post_selector = "div.thing.link"
            await page.wait_for_selector(post_selector, timeout=30000)

            posts = await page.query_selector_all(post_selector)

            for post in posts[:max_posts]:
                if stop_event and stop_event.is_set():
                    logging.info("Stop event received during post collection.")
                    break

                title_element = await post.query_selector('a.title')
                comments_element = await post.query_selector('a.comments')

                if title_element and comments_element:
                    post_links.append(await comments_element.get_attribute('href'))

            logging.info(f"Found {len(post_links)} posts to process.")

            # 3. Visit each post and scrape details and comments
            for i, link in enumerate(post_links):
                if stop_event and stop_event.is_set():
                    logging.info("Stop event received during comment collection.")
                    break

                logging.info(f"Processing post {i+1}/{len(post_links)}: {link}")
                await page.goto(link, wait_until="domcontentloaded")

                # Scrape post details
                post_element = await page.query_selector('div.thing.link')
                post_title = await (await post_element.query_selector('a.title')).inner_text()
                post_author = await (await post_element.query_selector('a.author')).inner_text()
                post_score = await (await post_element.query_selector('div.score.unvoted')).get_attribute('title')

                # Add post data
                all_data.append({
                    "Type": "Post",
                    "Author": post_author,
                    "Text": post_title,
                    "Score": int(post_score),
                    "URL": link
                })

                # Scrape top-level comments
                comment_elements = await page.query_selector_all('div.comment > div.entry')
                for comment in comment_elements:
                    try:
                        comment_author = await (await comment.query_selector('a.author')).inner_text()
                        comment_text = await (await comment.query_selector('div.md')).inner_html()
                        # Clean up comment text from HTML
                        comment_text = re.sub('<[^<]+?>', '', comment_text).strip()
                        comment_score_element = await comment.query_selector('span.score')
                        comment_score_text = await comment_score_element.inner_text()
                        comment_score = int(re.search(r'\d+', comment_score_text).group())

                        all_data.append({
                            "Type": "Comment",
                            "Author": comment_author,
                            "Text": comment_text,
                            "Score": comment_score,
                            "URL": link
                        })
                    except Exception:
                        logging.warning("Could not parse a comment, skipping.")

                await asyncio.sleep(1) # Be respectful to Reddit's servers

        except Exception as e:
            logging.error(f"An error occurred during Reddit scraping: {e}")
            screenshot_path = OUTPUT_DIR / "reddit_error_screenshot.png"
            await page.screenshot(path=screenshot_path)
            logging.info(f"An error screenshot has been saved as '{screenshot_path}'.")

        finally:
            await browser.close()
            logging.info("Browser closed.")

    if not all_data:
        return pd.DataFrame()

    return pd.DataFrame(all_data)

if __name__ == '__main__':
    async def main():
        print("Testing Reddit Scraper...")
        # Test 1: Scrape a subreddit
        df_subreddit = await scrape_reddit("indonesia", "Subreddit", max_posts=5)
        if not df_subreddit.empty:
            print("\n--- Subreddit Scrape Successful ---")
            print(f"Found {len(df_subreddit)} total items (posts and comments).")
            print(df_subreddit.head())
            df_subreddit.to_csv(OUTPUT_DIR / "reddit_subreddit_test.csv", index=False)
            print(f"Saved to {OUTPUT_DIR / 'reddit_subreddit_test.csv'}")
        else:
            print("\n--- Subreddit Scrape Failed ---")

        # Test 2: Scrape by search term
        df_search = await scrape_reddit("finansial", "Search", max_posts=5)
        if not df_search.empty:
            print("\n--- Search Scrape Successful ---")
            print(f"Found {len(df_search)} total items (posts and comments).")
            print(df_search.head())
            df_search.to_csv(OUTPUT_DIR / "reddit_search_test.csv", index=False)
            print(f"Saved to {OUTPUT_DIR / 'reddit_search_test.csv'}")
        else:
            print("\n--- Search Scrape Failed ---")

    asyncio.run(main())
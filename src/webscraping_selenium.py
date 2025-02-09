from dotenv import load_dotenv
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from urllib.parse import urlencode
from utils import save_tools

if os.path.exists(".env"):
    load_dotenv()
else:
    print("⚠️ Warning: .env file not found. Ensure your env keys are set in system environment variables.")

required_env_vars = ['NEWS_PAGE_URL']
for var in required_env_vars:
    if not os.getenv(var):
        raise Exception(f"Environment variable {var} is not set")

NEWS_PAGE_URL = os.getenv("NEWS_PAGE_URL")
PARAMS_TEMPLATE = {
    "kw": "\"jerónimo martins\"",       # or any other keyword
    "sort": "release_date desc",
    "pg": 1
}
PAGE_ELEMENTS_SELECTORS = {
    "container": '.search-results .article-category',
    "article": {
        "item-self": ".article",
        # all elements contain an anchor tag with the link to the article's page
        "title": "h3",                  # The title is inside an h3 tag
        "date": ".item-info a",         # The date is inside an anchor tag
        "summary": "div>div>a",         # The summary is inside an anchor tag two levels down the article root container
        # "news_page_url": "div>div>a"
    },
    "pagination": ".pagination .page-item:not(.active) a"
}

def build_search_url(keyword, page=1):
    params = PARAMS_TEMPLATE.copy()
    params["pg"] = page

    # build the url using the params dictionary and properly endcoded values for each key
    encoded_params = urlencode(params, safe='"')
    encoded_url = f"{NEWS_PAGE_URL}?{encoded_params}"
    print("🔍 Search URL:", encoded_url)
    return encoded_url

def scrape_news(driver, url):
    driver.get(url)
    time.sleep(6)  # Allow time for the page to load

    container_selector = PAGE_ELEMENTS_SELECTORS["container"]
    articles_selector = PAGE_ELEMENTS_SELECTORS["article"]["item-self"]
    all_articles_selector = f"{container_selector} {articles_selector}"
    articles = driver.find_elements(By.CSS_SELECTOR, all_articles_selector)
    news_data = []

    for article in articles:
        try:
            title_element = article.find_element(By.CSS_SELECTOR, PAGE_ELEMENTS_SELECTORS["article"]["title"])
            title = title_element.text
            main_link = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")

            date = article.find_element(By.CSS_SELECTOR, PAGE_ELEMENTS_SELECTORS["article"]["date"]).text

            # Extract summary (Ensure it's not an image link)
            summary_element = None
            all_links = article.find_elements(By.CSS_SELECTOR, PAGE_ELEMENTS_SELECTORS["article"]["summary"])
            for link in all_links:
                if link.text.strip():  # Only take links that have text content
                    summary_element = link
                    break
            
            if summary_element:
                summary = summary_element.text.strip()
                link = summary_element.get_attribute("href")
            else:
                summary = "N/A"
                link = main_link

            news_data.append({"Title": title, "Date": date, "Link": link, "Summary": summary})
        except Exception as e:
            print("❌ Skipping an article due to an error:", e)

    return news_data

def load_existing_news(filename):
    """Loads existing news from CSV if the file exists."""
    return save_tools.load_existing_dataframe(filename=filename, columns=["Title", "Date", "Link", "Summary"])

if __name__ == "__main__":
    keyword = input("What news are you searching for (e.g. \"jerónimo martins\"): ").strip()
    if not keyword:
        keyword = PARAMS_TEMPLATE["kw"]

    # User Input for Start Page
    try:
        start_page = int(input("Which page do you want to start scraping from (default: 1): ").strip())
    except ValueError:
        start_page = 1

    # User Input for Max Pages
    try:
        max_pages = int(input("How many pages do you want to scrape (default: 1, max: 30): ").strip())
        if max_pages < 1 or max_pages > 30:
            print("⚠️ Invalid input, setting max_pages to 1.")
            max_pages = 1
    except ValueError:
        max_pages = 1

    try:
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")
        driver = uc.Chrome(options=options)

        csv_filename = f"{keyword}_news.csv"

        existing_news_df = load_existing_news(csv_filename)
        existing_titles = set(existing_news_df["Title"].tolist())
        all_news_data = []

        current_page = start_page
        pages_scraped = 0

        while pages_scraped < max_pages:

            print(f"Current page: {current_page}")
            print(f"Max pages: {max_pages}")
            print(f"Scraped pages: {pages_scraped}");

            search_url = build_search_url(keyword, current_page)
            print(f"🔍 Scraping page {current_page}...")

            news_data = scrape_news(driver, search_url)
            if not news_data:
                print("No articles found on this page. Stopping search.")
                break

            # Filter out existing news
            new_articles = [article for article in news_data if article["Title"] not in existing_titles]
            all_news_data.extend(new_articles)

            if pages_scraped % 10 == 0 and pages_scraped > 0:
                cont = input(f"You have searched {pages_scraped} pages. Do you want to continue? (y/n): ").strip().lower()
                if cont != 'y':
                    print("Stopping search as per user request.")
                    break
            
            current_page += 1
            pages_scraped += 1
            #END WHILE LOOP

        if all_news_data:
            new_news_df = pd.DataFrame(all_news_data)
            updated_news_df = pd.concat([existing_news_df, new_news_df]).drop_duplicates(subset=["Title"], keep="first")

            save_tools.save_to_csv(updated_news_df, csv_filename, ignore_overwrite=True, append_data=False)
            print(f"✅ {len(new_news_df)} new articles added. News saved to {csv_filename}")
        else:
            print("No news articles found.")

    except Exception as err:
        print("❌ An error occurred:", err)

    finally:
        if driver:
            try:
                driver.quit()
                print("✅ WebDriver closed properly.")
            except Exception as e:
                print("❌ Error when quitting WebDriver:", e)
                try:
                    driver.close()
                    print("✅ WebDriver closed properly.")
                except Exception as e2:
                    print("❌ Error when closing WebDriver:", e2)
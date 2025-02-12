import os
import pytest
from urllib.parse import urlencode, quote_plus
from unittest.mock import patch
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
from dotenv import load_dotenv
from src.webscraping_selenium import (
    build_search_url,
    scrape_news,
    load_existing_news
)
from utils import save_tools

# Automatically load test environment variables from `.env.test`
@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Load environment variables for testing from .env.test file"""
    load_dotenv(".env.test")

@pytest.fixture
def mock_env():
    """Ensure environment variable is set"""
    assert os.getenv("NEWS_PAGE_URL") is not None, "NEWS_PAGE_URL is not set"

@pytest.fixture(scope="session")
def selenium_driver():
    """Initialize Selenium WebDriver in undetected mode for testing"""
    options = Options()
    options.add_argument("--headless=new")  # Run in headless mode for faster testing
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    yield driver
    driver.quit()

def test_build_search_url():
    """Test URL generation from webscraping_selenium.py"""
    params = {
        "kw": "\"jerónimo martins\"",
        "sort": "release_date desc",
        "pg": 1
    }
    keyword = "\"jerónimo martins\""
    page = 1

    url = build_search_url(params["kw"], params["pg"])
    
    encoded_keyword = quote_plus(keyword, '"')
    encoded_params = urlencode(params, safe='"')

    assert os.getenv("NEWS_PAGE_URL") in url, "NEWS_PAGE_URL is missing from generated URL"
    assert encoded_params in url, "URL parameters are not properly encoded"
    assert f"kw={encoded_keyword}" in url, "Keyword is not properly encoded in the URL"
    assert f"pg={page}" in url, "Page number is incorrect in URL"

def test_scrape_news(selenium_driver):
    """Test scraping news articles using Selenium and webscraping_selenium.py"""
    news_page_url = os.getenv("NEWS_PAGE_URL")
    assert news_page_url, "NEWS_PAGE_URL is not set in the environment"

    # selenium_driver.get(news_page_url)
    # time.sleep(5)  # Wait for the page to load completely

    search_url = build_search_url("\"jerónimo martins\"", 1)
    news_data = scrape_news(selenium_driver, search_url)

    assert len(news_data) > 0, "No articles found"
    
    first_article = news_data[0]
    assert "Title" in first_article, "Missing title in scraped article"
    assert "Link" in first_article and first_article["Link"].startswith("http"), "Invalid link in article"
    assert "Date" in first_article, "Missing date in scraped article"
    assert "Summary" in first_article, "Missing summary in scraped article"

    print(f"✅ Successfully scraped: {first_article['Title']} ({first_article['Date']}) - {first_article['Link']}")

@patch("utils.save_tools.load_existing_dataframe")
def test_load_existing_news(mock_load_csv):
    """Test loading existing news from CSV"""
    mock_data = pd.DataFrame({
        "Title": ["Existing Article"],
        "Date": ["2024-02-10"],
        "Link": ["https://example.com/existing"],
        "Summary": ["Existing Summary"]
    })
    mock_load_csv.return_value = mock_data

    df = load_existing_news("test_news.csv")
    assert not df.empty
    assert "Title" in df.columns
    assert df.iloc[0]["Title"] == "Existing Article"

@patch("utils.save_tools.save_to_csv")
def test_save_news(mock_save_csv):
    """Test saving news to CSV"""
    news_data = pd.DataFrame({
        "Title": ["New Article"],
        "Date": ["2024-02-11"],
        "Link": ["https://example.com/new"],
        "Summary": ["New Summary"]
    })

    save_tools.save_to_csv(news_data, "test_news.csv", ignore_overwrite=True, append_data=False)
    mock_save_csv.assert_called_once()

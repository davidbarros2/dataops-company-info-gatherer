from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def extract_news(driver, search_term):
    """
    Extract the title and body of the first news article containing the search term.
    If not found, it navigates to the next page and continues searching.
    """
    while True:
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all news articles on the page
        articles = soup.find_all('a', class_='card')  # Adjust class based on website structure
        
        for article in articles:
            title_tag = article.find('h2')
            if title_tag and search_term.lower() in title_tag.text.lower():
                # Click on the article link to open it
                article_url = article['href']
                driver.get(f"https://www.lusa.pt{article_url}")

                # Wait for the article page to load
                time.sleep(3)
                article_soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Extract title and body
                article_title = article_soup.find('h1')
                article_body = article_soup.find('div', class_='article-content')

                return {
                    'title': article_title.text.strip() if article_title else 'No Title Found',
                    'body': article_body.text.strip() if article_body else 'No Body Found'
                }

        # Check for 'Next' button to go to the next page
        next_page = soup.find('a', {'aria-label': 'Próxima'})  # Adjust if needed
        if next_page:
            driver.get(f"https://www.lusa.pt{next_page['href']}")
            time.sleep(3)
        else:
            return {'title': 'No articles found', 'body': 'No articles found'}

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Go to lusa.pt
    driver.get("https://www.lusa.pt/")

    # Wait for the cookie consent button to appear and click "Permitir todos"
    wait = WebDriverWait(driver, 10)
    try:
        accept_cookies_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Permitir todos')]")))
        accept_cookies_button.click()
        print("Cookies accepted.")
    except:
        print("No cookie consent popup found or already accepted.")

    # Wait for the search input to be visible
    search_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Pesquise aqui']")))

    # Enter search term and press Enter
    search_term = "Jerónimo Martins"
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)

    # Wait for search results to load
    time.sleep(5)

    # Extract news content using BeautifulSoup
    news = extract_news(driver, search_term)

    # Display the extracted news
    print(f"Title: {news['title']}\n")
    print(f"Body: {news['body']}")

finally:
    driver.quit() #fork clone e colocar la os ficheiros com o vosso codigo 

import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Initialize the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the website
driver.get("https://www.lusa.pt/search-results?kw=jer%C3%B3nimo%20martins")

# Wait for the page to load completely
time.sleep(5)  # Adjust this sleep time if necessary, or use WebDriverWait for a more reliable solution

# Extract all the <h3> elements, which contain the titles and their <a> links
titles = driver.find_elements(By.XPATH, "//h3/a")  # Find all <a> tags within <h3> tags

news_data = []

# Iterate over each title and extract the text and URL
for title_element in titles:
    try:
        # Extract title text (the text inside the <a> tag)
        title = title_element.text
    except:
        title = "No title found"  # If no title is found
    
    try:
        # Extract URL (from href attribute of the <a> tag)
        url = title_element.get_attribute("href")
    except:
        url = "No URL found"  # If no URL is found

    # Collect the article's title and URL
    news_data.append([title, url])

# File path for the CSV
file_path = r"C:\Users\david\jmt\data\news_titles_and_urls.csv"

# Write or append to the CSV file
with open(file_path, mode='a', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    
    # Check if the file is empty and write the header only once
    if file.tell() == 0:
        writer.writerow(['News Title', 'URL'])
    
    # Write the data to the CSV
    writer.writerows(news_data)

# Close the browser
driver.quit()

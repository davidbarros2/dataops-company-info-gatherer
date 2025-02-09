from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
import os

def scrape_lusa_with_selenium():
    """
    Faz scraping no site da Lusa.pt usando Selenium para buscar notícias sobre Jerónimo Martins.
    """
    url = "https://www.lusa.pt/search-results?kw=jer%C3%B3nimo%20martins"

    # Configurando o driver do Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Comente esta linha para depuração visual
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        print("Acessando a página...")
        driver.get(url)
        time.sleep(10)  # Tempo de espera para o carregamento da página
        print("Página carregada. Buscando notícias...")

        # XPath para capturar os artigos
        articles = driver.find_elements(By.XPATH, '//div[@class="article"]')

        news_list = []

        for article in articles:
            # Obtém o texto do título e o link
            title_element = article.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a')
            title = title_element.text.strip()
            
            # Obtém o URL
            link = title_element.get_attribute("href")
            
            # Obtém a data
            date_element = article.find_element(By.XPATH, './/ul[@class="list-inline item-info"]/li/a')
            date = date_element.text.strip()
            
            # Obtém a categoria
            category_element = article.find_element(By.XPATH, './/div[@class="col-sm-12"]/a')
            category = category_element.text.strip()

            if title and link and date and category:
                news_list.append(
                    {
                    "title": title, 
                    "link": link, 
                    "date": date, 
                    "category": category
                }
                )

        # Verifica se encontrou notícias
        if not news_list:
            print("Nenhuma notícia encontrada na Lusa.pt.")
            return

        # Salvando os resultados em CSV
        csv_dir = r"C:\Users\joana\Desktop\Company_Stock_Project\data" # Define o diretório para salvar o arquivo CSV
        os.makedirs(csv_dir, exist_ok=True) # Cria o diretório, se ele não existir
        csv_path = os.path.join(csv_dir, "lusa_jeronimo_martins_news.csv")# Define o caminho completo do arquivo CSV

        # Abre o arquivo CSV para escrita
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ["title", "link", "date", "category"]# Define os nomes das colunas do CSV
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)# Cria um objeto DictWriter com os nomes das colunas
            writer.writeheader()# Escreve o cabeçalho no arquivo CSV
            writer.writerows(news_list)# Escreve as linhas de notícias no arquivo CSV

        print(f"Notícias salvas em: {csv_path}")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_lusa_with_selenium()
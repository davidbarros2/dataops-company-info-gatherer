import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# URL do HTML hospedado localmente ou online
url = "https://www.x-rates.com/calculator/?from=EUR&to=USD&amount=1"

# Faz a requisição HTTP para obter o conteúdo do HTML
response = requests.get(url)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    # Parse do HTML usando BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Extrair o cambio
    exchange_rate_full = soup.find("span", class_="ccOutputRslt").text.strip()
    exchange_rate = exchange_rate_full.split(" ")[0] #grabs the first item which is the number we want

    # Extrair o código da moeda
    exchange_code = soup.find("span", class_="ccOutputCode").text.strip()

    # Extrair o timestamp
    timestamp = soup.find("span", class_="calOutputTS").text.strip()

    # Criar um dict com os dados extraídos 
    data = {
        "Exchange Rate": [exchange_rate],
        "Coin": [exchange_code],
        "Timestamp": [timestamp]
    }
    #Converter dict para dataframe
    df = pd.DataFrame(data)

    # Caminho para o arquivo CSV
    output_path = r"C:\Users\joana\Desktop\Company_Stock_Project\data\exchange_rates.csv"

    # Verifica se o arquivo CSV já existe
    if os.path.isfile(output_path):
        # Adiciona os dados ao arquivo existente
        df.to_csv(output_path, mode='a', header=False, index=False) #a--> append
    
    else:
        # Cria um novo arquivo CSV com cabeçalho
        df.to_csv(output_path, mode='w', header=True, index=False) #w--> write

    print(f"Exchange Rate EURO to USD: {exchange_rate}")
    print(f"Timestamp: {timestamp}")
    print(f"Dados adicionados ao arquivo CSV em: {output_path}")

else:
    print("Erro ao acessar a página:", response.status_code)


import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import time

# URL do site X-Rates para a taxa de conversão de Euro para Dólar
url = "https://www.x-rates.com/calculator/?from=EUR&to=USD&amount=1"

# Caminho do arquivo CSV
output_directory = r"C:\Users\david\jmt\data"
output_file = os.path.join(output_directory, "conversion_rates.csv")

# Garantir que o diretório de saída existe
os.makedirs(output_directory, exist_ok=True)

# Função para realizar a solicitação com tentativas e backoff exponencial
def fetch_conversion_rate(url, retries=5, delay=2):
    """
    Faz uma solicitação HTTP com tentativas e backoff exponencial em caso de falha.
    
    Args:
        url (str): URL para onde a solicitação será enviada.
        retries (int): Número de tentativas em caso de falha.
        delay (int): Tempo inicial de espera entre as tentativas (em segundos).
    
    Returns:
        str: Taxa de conversão ou None se falhar após o número de tentativas.
    """
    for attempt in range(retries):
        try:
            # Fazer a solicitação GET para obter o HTML da página
            response = requests.get(url)
            
            # Verificar se a solicitação foi bem-sucedida
            if response.status_code == 200:
                return response.text
            else:
                print(f"Erro ao acessar a página. Código de status: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"Erro na tentativa {attempt + 1}: {e}")
        
        # Espera antes da próxima tentativa (backoff exponencial)
        time.sleep(delay * (2 ** attempt))  # Aumenta o tempo de espera após cada falha
    
    print("Falha ao acessar a página após várias tentativas.")
    return None

# Função para verificar se a taxa de conversão já foi registrada
def is_duplicate(timestamp, conversion_rate, output_file):
    """
    Verifica se a taxa de conversão e timestamp já estão no arquivo CSV.
    
    Args:
        timestamp (str): Timestamp a ser verificado.
        conversion_rate (str): Taxa de conversão a ser verificada.
        output_file (str): Caminho do arquivo CSV onde os dados são armazenados.
    
    Returns:
        bool: True se já existir, False caso contrário.
    """
    if os.path.exists(output_file):
        with open(output_file, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                # Ignorar cabeçalhos
                if row[0] == "Timestamp":
                    continue
                # Verifica se já existe a mesma taxa de conversão e timestamp
                if row[0] == timestamp and row[1] == conversion_rate:
                    return True
    return False

# Solicitar e processar a taxa de conversão
response_text = fetch_conversion_rate(url)

if response_text:
    # Analisar o HTML com BeautifulSoup
    soup = BeautifulSoup(response_text, "html.parser")
    
    # Encontrar a taxa de conversão na página
    conversion_rate_element = soup.find("span", class_="ccOutputTrail")
    if conversion_rate_element:
        # Obter o valor completo da conversão
        conversion_rate = soup.find("span", class_="ccOutputRslt").text.strip() + conversion_rate_element.text.strip()
        
        # Obter o timestamp atual
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Verificar se os dados já foram registrados
        if not is_duplicate(timestamp, conversion_rate, output_file):
            # Adicionar os dados ao arquivo CSV
            with open(output_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                # Adicionar cabeçalhos somente se o arquivo estiver vazio
                if file.tell() == 0:  # Verifica se o arquivo está vazio
                    writer.writerow(["Timestamp", "Conversion Rate (EUR to USD)"])
                writer.writerow([timestamp, conversion_rate])
            
            # Mensagem de sucesso
            print(f"Taxa de conversão ({timestamp}): {conversion_rate}")
            print(f"Dados adicionados ao arquivo '{output_file}'.")
        else:
            print("A mesma taxa de conversão já foi registrada. Nenhum dado foi adicionado.")
    else:
        print("Não foi possível encontrar a taxa de conversão na página.")
else:
    print("Falha ao acessar a página após várias tentativas.")

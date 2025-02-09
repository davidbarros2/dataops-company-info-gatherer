import requests  # Biblioteca para realizar solicitações HTTP (ex.: buscar dados de uma API)
import pandas as pd  # Biblioteca para manipulação e análise de dados (DataFrames)
import os  # Biblioteca para interagir com o sistema de arquivos e variáveis de ambiente
from pathlib import Path  # Biblioteca para manipulação de caminhos de arquivos e pastas
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente a partir de um arquivo .env

# Carrega as variáveis de ambiente do arquivo .env (se existir)
if os.path.exists(".env"):
    load_dotenv()  # Carrega as variáveis do arquivo .env
else:
    print("Aviso: Arquivo .env não encontrado. Certifique-se de que as chaves da API estão configuradas nas variáveis de ambiente do sistema.")

# Recupera as variáveis de ambiente para a chave da API e URL da Alpha Vantage
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")  # Chave de acesso à API
URL = os.getenv("ALPHA_VANTAGE_URL")  # URL da API

# Função para buscar dados da API da Alpha Vantage
def fetch_stock_data(symbol):
    """
    Busca os dados mensais ajustados de ações na API Alpha Vantage.
    
    Args:
        symbol (str): Símbolo da ação que queremos buscar.
        
    Retorna:
        dict: Dados da ação em formato JSON, ou None em caso de erro.
    """
    # Define os parâmetros da solicitação para a API
    params = {
        'function': 'TIME_SERIES_MONTHLY_ADJUSTED',  # Tipo de dados: série temporal ajustada mensalmente
        'symbol': symbol,  # Símbolo da ação (ex.: GALP.LS)
        'apikey': API_KEY,  # Chave de acesso à API
        'datatype': 'json'  # Formato dos dados retornados (JSON)
    }

    # Faz a solicitação GET para a API com os parâmetros definidos
    response = requests.get(URL, params=params)
    
    # Verifica se a solicitação foi bem-sucedida (código HTTP 200)
    if response.status_code == 200:
        try:
            # Tenta converter a resposta da API de JSON para um dicionário Python
            data = response.json()
            
            # Verifica se a chave "Monthly Adjusted Time Series" existe nos dados retornados
            if "Monthly Adjusted Time Series" in data:
                return data["Monthly Adjusted Time Series"]  # Retorna apenas a parte relevante dos dados
            else:
                # Lança um erro se os dados esperados não estiverem presentes na resposta
                raise ValueError(f"Resposta inesperada: {data.get('Note', 'Dados ausentes')}")
        except ValueError as e:
            # Exibe um erro caso haja problemas ao interpretar os dados JSON
            print(f"Erro ao interpretar o JSON: {e}")
    else:
        # Exibe um erro caso a solicitação HTTP tenha falhado
        print(f"Erro ao buscar dados: Código {response.status_code}")
    
    # Retorna None caso ocorra qualquer erro
    return None

# Função para processar os dados recebidos e convertê-los em um DataFrame
def process_data(time_series):
    """
    Processa os dados da série temporal e os converte em um DataFrame do Pandas.
    
    Args:
        time_series (dict): Dados brutos de séries temporais da API.
        
    Retorna:
        pd.DataFrame: DataFrame processado com as colunas renomeadas e ordenadas.
    """
    # Converte o dicionário de séries temporais em um DataFrame do Pandas
    df = pd.DataFrame.from_dict(time_series, orient="index")

    # Converte o índice (datas) para o formato datetime (datas interpretáveis pelo Python)
    df.index = pd.to_datetime(df.index)
    
    # Nomeia o índice como "date" para representar as datas
    df.index.name = "date"
    
    # Mapeia os nomes das colunas para um formato mais amigável
    columns_mapping = {
        "1. open": "open",  # Preço de abertura
        "2. high": "high",  # Preço mais alto
        "3. low": "low",  # Preço mais baixo
        "4. close": "close",  # Preço de fechamento
        "5. adjusted close": "adjusted_close",  # Preço ajustado de fechamento
        "6. volume": "volume",  # Volume de ações negociadas
        "7. dividend amount": "dividend_amount"  # Valor dos dividendos
    }
    
    # Seleciona as colunas relevantes e renomeia usando o mapeamento acima
    df = df[list(columns_mapping.keys())].rename(columns=columns_mapping)
    
    # Ordena o DataFrame pelas datas (do mais antigo para o mais recente)
    return df.sort_index()

# Função para salvar os dados em um arquivo CSV
def save_to_csv(df, output_path):
    """
    Salva os dados de um DataFrame em um arquivo CSV.
    
    Args:
        df (pd.DataFrame): DataFrame contendo os dados das ações.
        output_path (str): Caminho para salvar o arquivo CSV.
    """
    # Garante que o diretório onde o arquivo será salvo exista
    output_dir = Path(output_path).parent  # Extrai o diretório do caminho fornecido
    output_dir.mkdir(parents=True, exist_ok=True)  # Cria o diretório, se necessário

    # Salva o DataFrame em um arquivo CSV
    df.to_csv(output_path)

    # Exibe uma mensagem indicando que os dados foram salvos com sucesso
    print(f"Dados salvos com sucesso em {output_path}")

# Função para ler o símbolo da ação a partir da entrada do usuário
def read_symbol():
    """
    Solicita ao usuário um símbolo de ação ou usa um símbolo padrão.
    
    Retorna:
        str: Símbolo da ação (ex.: "JMT.LS").
    """
    # Solicita o símbolo da ação ao usuário
    symbol = input("Digite o símbolo da ação ou pressione Enter para usar o padrão (JMT.LS): ").strip()
    return symbol if symbol else "JMT.LS"  # Retorna o símbolo fornecido ou o padrão

# Função principal que organiza e executa o programa
def main():
    """
    Função principal que executa o fluxo completo do programa.
    """
    # Obtém o símbolo da ação a ser buscado, com opção de usar um valor padrão
    symbol = read_symbol()  # Obtém o símbolo da ação do usuário ou usa o padrão

    # Busca os dados da API para o símbolo fornecido
    time_series = fetch_stock_data(symbol)
    
    # Verifica se os dados foram recuperados com sucesso
    if time_series:
        # Processa os dados para criar um DataFrame
        df = process_data(time_series)
        
        # Define o caminho para salvar o arquivo CSV
        output_path = r"./data/monthly_adjusted_data.csv"  # Caminho para salvar o arquivo (modifique conforme necessário)
        
        # Salva os dados no arquivo CSV
        save_to_csv(df, output_path)
        
        # Exibe as primeiras 5 linhas do DataFrame no console
        print(df.head())
    else:
        # Exibe uma mensagem de erro caso a busca dos dados tenha falhado
        print("Falha ao buscar os dados da ação.")

# Garante que o programa só será executado se for chamado diretamente (não importado)
if __name__ == "__main__":
    main()  # Chama a função principal para executar o programa

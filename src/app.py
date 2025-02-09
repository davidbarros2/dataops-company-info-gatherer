import requests  # Biblioteca para realizar solicitações HTTP (ex.: buscar dados de uma API)
import pandas as pd  # Biblioteca para manipulação e análise de dados (DataFrames)
from pathlib import Path  # Biblioteca para manipulação de caminhos de arquivos e pastas

# Função para buscar os dados da API
def fetch_stock_data(symbol, api_key):
    """
    Busca dados de ações ajustados mensalmente na API Alpha Vantage.

    Args:
        symbol (str): Símbolo da ação (ex.: GALP.LS).
        api_key (str): Chave de acesso da API.

    Returns:
        dict: Dados JSON da API contendo informações da ação.
    """
    # URL da API
    url = 'https://www.alphavantage.co/query'

    # Parâmetros para a solicitação (definem o que será buscado)
    params = {
        'function': 'TIME_SERIES_MONTHLY_ADJUSTED',  # Tipo de dados: série temporal ajustada mensalmente
        'symbol': symbol,  # O símbolo da ação (ex.: GALP.LS)
        'apikey': api_key,  # A chave de acesso à API
        'datatype': 'json'  # O formato de saída dos dados (JSON)
    }

    # Faz a solicitação GET para a API com os parâmetros
    response = requests.get(url, params=params)
    
    # Verifica se a solicitação foi bem-sucedida (código de status HTTP 200)
    if response.status_code == 200:
        try:
            # Converte a resposta da API em um dicionário Python
            data = response.json()
            
            # Verifica se os dados esperados estão na resposta
            if "Monthly Adjusted Time Series" in data:
                return data["Monthly Adjusted Time Series"]  # Retorna apenas a parte útil dos dados
            else:
                # Caso os dados esperados não estejam presentes, lança um erro
                raise ValueError(f"Resposta inesperada: {data.get('Note', 'Dados ausentes')}")
        except ValueError as e:
            # Mostra um erro caso haja problemas ao interpretar os dados JSON
            print(f"Erro ao interpretar o JSON: {e}")
    else:
        # Exibe uma mensagem de erro caso a solicitação HTTP falhe
        print(f"Erro ao buscar dados: Código {response.status_code}")
    
    # Retorna None se algo deu errado
    return None


# Função para processar os dados recebidos
def process_data(time_series):
    """
    Converte dados de séries temporais em um DataFrame do Pandas.

    Args:
        time_series (dict): Dados brutos de séries temporais da API.

    Returns:
        pd.DataFrame: DataFrame processado com colunas renomeadas e ordenadas.
    """
    # Converte o dicionário de séries temporais em um DataFrame do Pandas
    df = pd.DataFrame.from_dict(time_series, orient="index")

    # Converte o índice (datas) para o formato datetime (datas interpretáveis pelo Python)
    df.index = pd.to_datetime(df.index)
    
    # Nomeia o índice como "date" para representar as datas
    df.index.name = "date"

    # Seleciona e renomeia as colunas para um formato mais amigável
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


# Função para salvar os dados processados em um arquivo CSV
def save_to_csv(df, output_path):
    """
    Salva o DataFrame em um arquivo CSV.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados das ações.
        output_path (str): Caminho para salvar o arquivo CSV.
    """
    # Garante que a pasta onde o arquivo será salvo existe
    output_dir = Path(output_path).parent  # Extrai o diretório do caminho fornecido
    output_dir.mkdir(parents=True, exist_ok=True)  # Cria a pasta, se necessário

    # Salva o DataFrame em um arquivo CSV
    df.to_csv(output_path)

    # Mostra uma mensagem indicando que os dados foram salvos
    print(f"Dados salvos com sucesso em {output_path}")


# Função principal que organiza e executa o programa
def main():
    # Configurações
    api_key = 'P331A6UMPC721HB6'  # Sua chave de acesso à API
    symbol = 'JMT.LS'  # O símbolo da ação que queremos buscar
    output_path = r"C:\Users\david\jmt\data\monthly_adjusted_data.csv"  # Caminho para salvar o CSV

    # Busca os dados da API
    time_series = fetch_stock_data(symbol, api_key)
    
    # Verifica se os dados foram recuperados com sucesso
    if time_series:
        # Processa os dados brutos em um DataFrame
        df = process_data(time_series)
        
        # Salva o DataFrame processado em um arquivo CSV
        save_to_csv(df, output_path)
        
        # Mostra os 5 primeiros registros do DataFrame no console
        print(df.head())
    else:
        # Exibe uma mensagem de erro se a busca dos dados falhou
        print("Falha ao buscar os dados da ação.")


# Garante que o programa só será executado se for chamado diretamente (não importado)
if __name__ == "__main__":
    main()

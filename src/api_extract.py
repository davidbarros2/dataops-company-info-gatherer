import os
import requests
import pandas as pd

# Função para buscar os dados mensais ajustados
def fetch_monthly_adjusted_data(symbol='JMT.LS'):
    """
    Coleta dados overview da Alpha Vantage e retorna um DataFrame.
    A chave da API é lida da variável de ambiente 'API_KEY_JMS'.
    """
    # Obtém a chave da API da variável de ambiente
    api_key = os.getenv('API_KEY_JMS')
    if not api_key:
        raise ValueError(
            "A API Key não está definida. Configure a variável de ambiente 'API_KEY_JMS'."
            )

    url = "https://www.alphavantage.co/query"
    
    params = {
        "function": "TIME_SERIES_MONTHLY_ADJUSTED",
        "symbol": symbol,
        "apikey": api_key,
        "datatype": "json",
    }

    # Fazendo a solicitação à API
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Garante erro caso a solicitação falhe
        data = response.json()

        if "Monthly Adjusted Time Series" not in data:
            raise ValueError(
                "Erro: Dados não encontrados para o símbolo fornecido"
            )

        # Processando os dados
        time_series = data["Monthly Adjusted Time Series"]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)  # Converte o índice para datetime
        df.index.name = "date"  # Nomeia o índice como 'date'

        # Seleciona as colunas relevantes
        df = df[["1. open", "2. high", "3. low", "4. close",
                 "5. adjusted close", "6. volume", "7. dividend amount"]]
        #Creates a new DataFrame that contains only the columns specified within the double square brackets.
        #The double square brackets are used to select multiple columns in a pandas DataFrame.
        #When you use a single set of square brackets with the column name, you get a Series.
        
        df.columns = ["open", "high", "low", "close",
                      "adjusted_close", "volume", "dividend_amount"] #rename columns
        
        df = df.sort_index()  # Ordena por data

        return df

    except requests.RequestException as e:
        print(f"Erro na solicitação à API: {e}")
        return None
    
    except ValueError as e:
        print(f"Erro nos dados recebidos: {e}")
        return None
    
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

# Função para salvar os dados em um arquivo CSV
def save_to_csv(df, output_path):
    """
    Salva um DataFrame em um arquivo CSV.
    """
    try:
        df.to_csv(output_path)
        print(f"Dados salvos em: {output_path}")

    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")


# Ponto de entrada do programa
if __name__ == "__main__":
    df_monthly = fetch_monthly_adjusted_data()  # Fixed: Added parentheses to call the function

    if df_monthly is not None:
        output_path = r"C:\Users\joana\Desktop\Company_Stock_Project\data\monthly_adjusted_data.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        save_to_csv(df_monthly, output_path)
        print(df_monthly.head())
    
    else:
        print("Erro ao buscar os dados mensais. Nenhum CSV foi gerado.")


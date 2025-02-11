import pytest
import pandas as pd
import requests
import os
from unittest.mock import patch, MagicMock
from api_v2 import fetch_stock_data, process_data, read_symbol, save_to_csv

# Dados simulados para a resposta da API (usado para testar a função process_data)
MOCK_TIME_SERIES = {
    "2024-01-01": {
        "1. open": "150.00",  # Preço de abertura
        "2. high": "155.00",  # Preço mais alto do dia
        "3. low": "148.50",  # Preço mais baixo do dia
        "4. close": "153.75",  # Preço de fechamento
        "5. adjusted close": "153.75",  # Preço ajustado de fechamento
        "6. volume": "1234567",  # Volume de negociações
        "7. dividend amount": "0.50"  # Valor dos dividendos
    }
}

@pytest.fixture # A variável 'sample_dataframe' será passada automaticamente para os testes que utilizarem esse fixture.
def sample_dataframe():
    """Cria um DataFrame de exemplo processado a partir dos dados simulados"""
    return process_data(MOCK_TIME_SERIES)

# Teste para verificar se a função fetch_stock_data consegue ir buscar e processar os dados da API corretamente
@patch("api_v2.requests.get")  # Substitui requests.get por um mock
def test_fetch_stock_data_success(mock_get):
    """Testa se fetch_stock_data() retorna os dados corretos quando a API responde corretamente"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Monthly Adjusted Time Series": MOCK_TIME_SERIES}
    
    mock_get.return_value = mock_response  
    result = fetch_stock_data("AAPL")  

    assert result is not None
    assert "2024-01-01" in result  
    assert "1. open" in result["2024-01-01"]  

# Teste para verificar se a função fetch_stock_data lida corretamente com falhas na API
@patch("api_v2.requests.get")
def test_fetch_stock_data_failure(mock_get):
    """Testa se fetch_stock_data() retorna None quando a API falha"""
    mock_response = MagicMock()
    mock_response.status_code = 500  
    mock_get.return_value = mock_response
    
    result = fetch_stock_data("AAPL")  
    assert result is None  

# Teste para verificar a estrutura do DataFrame gerado pela função process_data()
def test_process_data_structure(sample_dataframe):
    """Testa se process_data() retorna um DataFrame bem estruturado"""
    assert isinstance(sample_dataframe, pd.DataFrame)  
    expected_columns = ["open", "high", "low", "close", "adjusted_close"]
    for col in expected_columns:
        assert col in sample_dataframe.columns  

# Teste para garantir que todos os valores processados são maiores que zero
def test_process_data_price_positive(sample_dataframe):
    """Testa se os preços das ações são sempre maiores que zero"""
    sample_dataframe[["open", "high", "low", "close", "adjusted_close"]] = \
        sample_dataframe[["open", "high", "low", "close", "adjusted_close"]].astype(float) # Preciso converter para float para não existir erros na comparação
    assert (sample_dataframe[["open", "high", "low", "close", "adjusted_close"]] > 0).all().all()

# Teste para verificar se o índice do DataFrame é do tipo datetime
def test_process_data_datetime(sample_dataframe):
    """Testa se o índice do DataFrame é uma data válida"""
    assert pd.api.types.is_datetime64_any_dtype(sample_dataframe.index)

# Teste para garantir que read_symbol() retorna o valor padrão "JMT.LS" quando não há user input em contrário
@patch("builtins.input", return_value="")
def test_read_symbol_default(mock_input):
    """Testa se read_symbol() retorna 'JMT.LS' quando o usuário não digita nada"""
    assert read_symbol() == "JMT.LS"

# Teste para garantir que read_symbol() retorna o valor do user input
@patch("builtins.input", return_value="AAPL")
def test_read_symbol_custom(mock_input):
    """Testa se read_symbol() retorna o valor digitado pelo usuário"""
    assert read_symbol() == "AAPL"

# Teste para verificar se a função save_to_csv chama corretamente o método to_csv() do Pandas
@patch("pandas.DataFrame.to_csv")  
@patch("builtins.input", return_value="")  
def test_save_to_csv(mock_input, mock_to_csv, sample_dataframe):
    """Testa se save_to_csv() chama corretamente o método DataFrame.to_csv()"""
    save_to_csv(sample_dataframe, "AAPL")  
    mock_to_csv.assert_called_once()

# Teste para garantir que fetch_stock_data() retorna None quando a API responde com um JSON vazio
@patch("api_v2.requests.get")  # Mock da requisição HTTP
def test_fetch_stock_data_empty_response(mock_get):
    """Testa se fetch_stock_data() retorna None quando a API responde com um JSON vazio"""
    
    # Simula uma resposta da API com status 200, mas sem dados na chave esperada
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}  # JSON vazio

    mock_get.return_value = mock_response  # Define o mock como resposta da requisição
    
    # Chama a função e verifica se ela retorna None ao invés de breakar
    result = fetch_stock_data("AAPL")
    assert result is None

# Teste para garantir que process_data() retorna um DataFrame vazio ao receber dados malformados
def test_process_data_invalid_data():
    """Testa se process_data() retorna um DataFrame vazio ao receber dados malformados"""

    # Cria um dicionário com um formato incorreto (falta a chave de preços)
    invalid_data = {
        "2024-01-01": {"random_key": "value"}
    }

    try:
        # Chama a função process_data com os dados inválidos
        df = process_data(invalid_data)
        
        # O DataFrame gerado deve estar vazio
        assert df.empty
    except KeyError:
        # Se ocorrer um erro de chave, deve ser tratado de forma controlada
        assert True  # A falha controlada é esperada no caso de dados inválidos

# Teste para verificar se save_to_csv() realmente está a criar um arquivo CSV no sistema de arquivos
@patch("builtins.input", return_value="")  # Mock de input para evitar a leitura do usuário
def test_save_to_csv_creates_file(mock_input, sample_dataframe):
    """Testa se save_to_csv() realmente cria um arquivo CSV no sistema de arquivos"""
    
    # Garantir que a folder 'data' existe
    os.makedirs('./data', exist_ok=True)

    # Use o nome correto do arquivo gerado pela função save_to_csv
    filename = "./data/AAPL_monthly_adjusted_data.csv"  # Nome correto do arquivo gerado

    # Chama a função para salvar os dados
    save_to_csv(sample_dataframe, "AAPL")

    # Verifica se o arquivo foi criado
    assert os.path.exists(filename)

    # Remove o arquivo após o teste para não poluir o diretório
    os.remove(filename)
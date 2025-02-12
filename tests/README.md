# 📌 teste_api_v2.py -> Resumo dos testes

Para executar os testes, utilize o comando `pytest` ou `pytest -v` (modo verbose) no seu terminal.

- **Comando**:  
  ```bash
  pytest

| 📝 Teste                                | ✅ O que ele verifica?                                                        |
|----------------------------------------|-------------------------------------------------------------------------------|
| `test_fetch_stock_data_success`        | Testa se `fetch_stock_data()` retorna os dados corretos quando a API responde corretamente. |
| `test_fetch_stock_data_failure`        | Testa se `fetch_stock_data()` retorna `None` quando a API falha (status code 500). |
| `test_process_data_structure`          | Testa se `process_data()` retorna um DataFrame bem estruturado com as colunas esperadas. |
| `test_process_data_price_positive`     | Testa se os preços das ações são sempre maiores que zero no DataFrame gerado. |
| `test_process_data_datetime`           | Testa se o índice do DataFrame gerado pela `process_data()` é do tipo `datetime`. |
| `test_read_symbol_default`             | Testa se `read_symbol()` retorna o valor padrão "JMT.LS" quando não há entrada do usuário. |
| `test_read_symbol_custom`              | Testa se `read_symbol()` retorna o valor digitado pelo usuário. |
| `test_save_to_csv`                     | Testa se `save_to_csv()` chama corretamente o método `to_csv()` do pandas para salvar o DataFrame em um arquivo CSV. |
| `test_fetch_stock_data_empty_response` | Testa se `fetch_stock_data()` retorna `None` quando a API responde com um JSON vazio. |
| `test_process_data_invalid_data`       | Testa se `process_data()` retorna um DataFrame vazio ao receber dados malformados (sem a chave de preços). |
| `test_save_to_csv_creates_file`        | Testa se `save_to_csv()` realmente cria um arquivo CSV no sistema de arquivos, verificando sua existência. |

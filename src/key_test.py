import os

api_key = os.environ.get("API_KEY_JMS")

if api_key:
    print(f"Sua API Key foi carregada com sucesso!")
else:
    print("Erro: API_KEY_GALP não está definida!")

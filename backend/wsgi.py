import os
from dotenv import load_dotenv
from app import create_app

# Carrega variáveis do .env na raiz do projeto se existir
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"🚀 Iniciando Akademus API em http://{host}:{port}")
    app.run(host=host, port=port, debug=True)

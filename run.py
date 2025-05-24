from app import create_app
from dotenv import load_dotenv

# Cargar variables de entorno al inicio
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
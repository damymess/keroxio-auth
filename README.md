# keroxio-auth

Microservice Keroxio - auth.keroxio.fr

## Deploiement Coolify

1. Connecter ce repo dans Coolify
2. Configurer les variables d'environnement (voir .env.example)
3. Deployer

## Developpement local

```bash
# Avec Docker
docker build -t keroxio-auth .
docker run -p 8000:8000 keroxio-auth

# Sans Docker (Python)
pip install -r requirements.txt
uvicorn main:app --reload
```

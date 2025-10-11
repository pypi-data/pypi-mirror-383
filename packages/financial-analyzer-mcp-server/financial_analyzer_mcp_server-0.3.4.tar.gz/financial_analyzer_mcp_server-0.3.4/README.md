# Financial Analyzer MCP Server

Un serveur Python pour le composant "financial-analyzer-mcp-server" (paquet distributable). Ce README décrit l'installation, la construction et la publication du paquet.

## Prérequis

- Python 3.8+ (ajuster selon vos besoins)
- virtualenv ou venv
- pip
- Outils de packaging : build, twine (installables via pip)

Installer les outils nécessaires :

```bash
python -m pip install --upgrade pip build twine
```

## Préparer l'environnement de développement

1. Créer et activer un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate     # Windows (PowerShell/CMD)
```

2. (Optionnel) Installer les dépendances de développement si présentes :

```bash
pip install -r requirements-dev.txt
```

## Commandes utiles

- Nettoyer les artefacts de build :

```bash
rm -rf dist/ build/ *.egg-info
```

- Construire le paquet :

```bash
python -m build
```

- Publier sur PyPI :

```bash
twine upload dist/*
```

- Publier sur Test PyPI (pour tests) :

```bash
twine upload --repository testpypi dist/*
```

## Exemples d'utilisation

Remplacez `votre_cle_api_mcpo` par votre clé API réelle.

- Lancer le service (mode production) :

```bash
uvx mcpo \
    --port 8000 \
    --api-key "votre_cle_api_mcpo" \
    -- \
    uvx \
    financial-analyzer-mcp-server
```

- Lancer le service en test (utilise Test PyPI pour le paquet) :

```bash
uvx mcpo \
    --port 8000 \
    --api-key "votre_cle_api_mcpo" \
    -- \
    uvx \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    --index-strategy unsafe-best-match \
    financial-analyzer-mcp-server@0.2.1
```

## Bonnes pratiques

- Versionnez le paquet avant publication (mettre à jour la version dans setup.py / pyproject.toml).
- Testez la construction localement (`python -m build`) et vérifiez le contenu de `dist/`.
- Utilisez Test PyPI pour valider la publication avant d'envoyer sur le dépôt officiel.

## Dépannage rapide

- Erreur d'authentification twine : configurez vos identifiants dans `~/.pypirc` ou fournissez `--username`/`--password` à twine.
- Version déjà publiée : incrémentez la version du paquet.
- Problèmes avec les dépendances : vérifiez `pyproject.toml` / `setup.cfg` et les index utilisés (extra-index-url).

---

## Deploying in Production (Example)
Deploying your MCP-to-OpenAPI proxy (powered by mcpo) is straightforward. Here's how to easily Dockerize and deploy it to cloud or VPS solutions:

🐳 Dockerize your Proxy Server using mcpo
Dockerfile Example
Create the following Dockerfile inside your deployment directory:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install mcpo uv
# Replace with your MCP server command; example: uvx mcp-server-time
CMD ["uvx", "mcpo", "--host", "0.0.0.0", "--port", "8000", "--", "uvx", "financial-analyzer-mcp-server"]
```

Build & Run the Container Locally
```bash
docker build -t mcp-proxy-server .
docker run -d -p 8000:8000 mcp-proxy-server
```

Deploying Your Container
Push to DockerHub or another registry:

```bash
docker tag mcp-proxy-server yourdockerusername/mcp-proxy-server:latest
docker push yourdockerusername/mcp-proxy-server:latest
```

All in one command
```bash
docker run -d -p 8000:8000 gara420/financial_analyzer_server:latest
```

Deploy using Docker Compose, Kubernetes YAML manifests, or your favorite cloud container services (AWS ECS, Azure Container Instances, Render.com, or Heroku).

✔️ Your production MCP servers are now effortlessly available via REST APIs!

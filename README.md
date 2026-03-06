# RunPod Ollama Serverless

Déploiement serverless d'Ollama sur RunPod.io pour exécuter des modèles LLM.

## 🚀 Fonctionnalités

- ✅ Configuration via variables d'environnement
- ✅ Authentification par API key
- ✅ Support de tous les modèles Ollama (texte + vision)
- ✅ **Analyse d'images avec modèles de vision** (llama3.2-vision, llava, etc.)
- ✅ Gestion des erreurs robuste
- ✅ Métriques de performance (durée, tokens, etc.)

## 📋 Configuration

### Variables d'environnement

Copiez `.env.example` vers `.env` et configurez :

```bash
# Modèle par défaut
DEFAULT_MODEL=llama3.2:3b

# Paramètres par défaut
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=512

# Sécurité (optionnel mais recommandé)
RUNPOD_API_KEY=your_secret_key
```

### Configuration sur RunPod

1. Créez un nouveau endpoint serverless sur [RunPod.io](https://runpod.io)
2. Configurez votre image Docker depuis ce dépôt
3. Ajoutez les variables d'environnement dans l'interface RunPod
4. Déployez !

## 🔧 Utilisation

### Format de requête

```json
{
  "input": {
    "api_key": "your_secret_key",
    "prompt": "Explique les interruptions ESP32",
    "model": "llama3.2:3b",
    "temperature": 0.7,
    "max_tokens": 512
  }
}
```

### Champs requis

- `prompt` : Votre question ou prompt (obligatoire)

### Champs optionnels

- `api_key` : Clé API pour l'authentification (requis si `RUNPOD_API_KEY` est défini)
- `model` : Modèle à utiliser (défaut : `DEFAULT_MODEL`)
- `temperature` : Contrôle la créativité (0.0 - 1.0, défaut : 0.7)
- `max_tokens` : Nombre maximum de tokens à générer (défaut : 512)
- `top_p` : Nucleus sampling (0.0 - 1.0)
- `top_k` : Top-K sampling (entier)
- `repeat_penalty` : Pénalité de répétition (float)

### Exemple de requête Python

```python
import requests

url = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"

payload = {
    "input": {
        "api_key": "your_secret_key",
        "prompt": "Qu'est-ce que l'intelligence artificielle?",
        "model": "llama3.2:3b",
        "temperature": 0.7,
        "max_tokens": 256
    }
}

headers = {
    "Authorization": "Bearer YOUR_RUNPOD_TOKEN",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### Exemple de requête cURL

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_RUNPOD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "api_key": "your_secret_key",
      "prompt": "Explique les interruptions ESP32",
      "temperature": 0.1,
      "max_tokens": 256
    }
  }'
```

### Format de réponse

```json
{
  "response": "Texte généré par le modèle",
  "model": "llama3.2:3b",
  "done": true,
  "total_duration": 1234567890,
  "load_duration": 123456789,
  "prompt_eval_count": 10,
  "eval_count": 50
}
```

## �️ Modèles de Vision (Analyse d'images)

Les modèles de vision permettent d'analyser des images et de répondre à des questions sur leur contenu.

### Modèles de vision supportés

- `llama3.2-vision` (recommandé) - Modèle multimodal de Meta
- `llava:7b`, `llava:13b`, `llava:34b` - LLaVA (Large Language and Vision Assistant)
- `bakllava` - Version améliorée de LLaVA
- `moondream` - Modèle compact et rapide
- `cogvlm` - Modèle de vision avancé

### Format de requête pour l'analyse d'images

```json
{
  "input": {
    "api_key": "your_secret_key",
    "model": "llama3.2-vision",
    "prompt": "Décris cette image en détail",
    "images": ["base64_encoded_image_data"],
    "temperature": 0.3,
    "max_tokens": 512
  }
}
```

### Formats d'images supportés

1. **Base64 pur** : `"iVBORw0KGgoAAAANSUhEUgAAAA..."`
2. **Data URI** : `"data:image/png;base64,iVBORw0KGgo..."`
3. **URL** : `"https://example.com/image.jpg"` (téléchargée et convertie automatiquement)

### Exemple Python avec image locale

```python
import requests
import base64

# Charger et encoder l'image
with open("photo.jpg", "rb") as img_file:
    image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

url = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"

payload = {
    "input": {
        "api_key": "your_secret_key",
        "model": "llama3.2-vision",
        "prompt": "Que vois-tu sur cette image?",
        "images": [image_base64],
        "temperature": 0.3,
        "max_tokens": 512
    }
}

headers = {
    "Authorization": "Bearer YOUR_RUNPOD_TOKEN",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print(result["output"]["response"])
```

### Utiliser le client vision

```bash
# Configurer les variables d'environnement
export RUNPOD_ENDPOINT_ID="votre-endpoint-id"
export RUNPOD_TOKEN="votre-token"
export RUNPOD_API_KEY="votre-cle-secrete"

# Analyser une image locale
./vision_client.py photo.jpg "Décris cette image"

# Analyser une image depuis une URL
./vision_client.py https://example.com/image.png "Que vois-tu?"
```

### Exemples de prompts pour l'analyse d'images

```python
# Description générale
"Décris cette image en détail"

# Question spécifique
"Combien de personnes sont présentes sur cette photo?"

# Analyse technique
"Identifie tous les objets visibles dans cette image"

# Lecture de texte (OCR)
"Lis et transcris tout le texte présent dans cette image"

# Analyse de graphique
"Explique ce que montre ce graphique"

# Multiple images
{
    "images": ["image1_base64", "image2_base64"],
    "prompt": "Compare ces deux images et décris leurs différences"
}
```

### Configuration pour les modèles de vision

Ajoutez cette variable d'environnement sur RunPod :

```bash
DEFAULT_VISION_MODEL=llama3.2-vision
```

### Recommandations GPU pour la vision

| Modèle | GPU recommandé | VRAM requise |
|--------|----------------|--------------|
| llama3.2-vision | RTX 4090 (24GB) | ~12-16GB |
| llava:7b | RTX 3090 (24GB) | ~10GB |
| llava:13b | A6000 (48GB) | ~18GB |
| moondream | RTX 3090 (24GB) | ~8GB |

## �🔒 Sécurité

### Activer l'authentification

1. Définissez `RUNPOD_API_KEY` dans vos variables d'environnement RunPod
2. Incluez cette clé dans toutes vos requêtes via le champ `api_key`

Sans cette configuration, l'endpoint sera accessible sans authentification (non recommandé en production).

## 🛠️ Développement local

### Test en local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Démarrer Ollama
ollama serve

# Dans un autre terminal, tester le handler
python handler.py
```

### Builder l'image Docker

```bash
docker build -t rp-ollama .
docker run -e DEFAULT_MODEL=llama3.2:3b rp-ollama
```

## 📦 Modèles supportés

Tous les modèles disponibles sur [Ollama Library](https://ollama.ai/library) :

- llama3.2:3b
- llama3:8b
- mistral
- mixtral
- codellama
- gemma
- etc.

**Note** : Le modèle sera téléchargé au premier démarrage. Pour les gros modèles, prévoyez suffisamment d'espace disque et de mémoire GPU.

## 🐛 Débogage

### Vérifier les logs RunPod

Les logs sont disponibles dans l'interface RunPod. Recherchez :
- `Starting Ollama server...`
- `Ollama is ready!`
- `Pulling default model: ...`
- `Starting RunPod handler...`

### Erreurs courantes

**401 - Invalid API key** : Vérifiez que votre `api_key` correspond à `RUNPOD_API_KEY`

**400 - Prompt is required** : Le champ `prompt` est manquant

**504 - Request timeout** : Le modèle met trop de temps à répondre (augmentez les ressources GPU)

**500 - Ollama API error** : Vérifiez que le modèle existe et est téléchargé

## 📝 License

MIT

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

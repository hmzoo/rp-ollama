# 👁️ Guide d'utilisation des modèles de vision

Ce guide vous explique comment utiliser les modèles de vision Ollama pour analyser des images.

## 🎯 Cas d'usage

Les modèles de vision peuvent :

- 📸 **Décrire des images** : Description détaillée du contenu visuel
- 🔍 **Détecter des objets** : Identifier et compter les objets présents
- 📝 **OCR (lecture de texte)** : Extraire le texte des images
- 📊 **Analyser des graphiques** : Interpréter des données visuelles
- 🎨 **Analyse artistique** : Commenter le style, les couleurs, la composition
- 🏥 **Images médicales** : Décrire des radiographies, scans (information seulement)
- 🛠️ **Inspection technique** : Analyser des diagrammes, schémas, plans
- 🌍 **Reconnaissance de lieux** : Identifier des monuments, paysages

## 🚀 Démarrage rapide

### 1. Configuration

```bash
# Variables d'environnement nécessaires
export RUNPOD_ENDPOINT_ID="votre-endpoint-id"
export RUNPOD_TOKEN="votre-token-runpod"
export RUNPOD_API_KEY="votre-cle-api"
```

### 2. Utilisation du client Python

```bash
# Analyser une image locale
./vision_client.py photo.jpg "Décris cette image"

# Depuis une URL
./vision_client.py https://example.com/image.png "Que vois-tu?"

# Avec un prompt personnalisé
./vision_client.py schema.png "Explique ce diagramme technique"
```

### 3. Exemple de code Python

```python
import requests
import base64

def analyze_image(image_path: str, prompt: str):
    # Charger l'image en base64
    with open(image_path, 'rb') as f:
        image_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Requête
    url = "https://api.runpod.ai/v2/YOUR_ENDPOINT/runsync"
    
    payload = {
        "input": {
            "api_key": "your_api_key",
            "model": "llama3.2-vision",
            "prompt": prompt,
            "images": [image_b64],
            "temperature": 0.3,
            "max_tokens": 512
        }
    }
    
    headers = {
        "Authorization": "Bearer YOUR_RUNPOD_TOKEN",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Utilisation
result = analyze_image("photo.jpg", "Décris cette image")
print(result["output"]["response"])
```

## 🤖 Choix du modèle

### Comparaison des modèles

| Modèle | Qualité | Vitesse | VRAM | Usage recommandé |
|--------|---------|---------|------|------------------|
| `llama3.2-vision` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 12-16GB | Usage général, recommandé |
| `llava:7b` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 10GB | Bon équilibre qualité/vitesse |
| `llava:13b` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 18GB | Haute qualité |
| `moondream` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 8GB | Rapide, pour des tâches simples |
| `bakllava` | ⭐⭐⭐⭐ | ⭐⭐⭐ | 12GB | Alternative à LLaVA |

### Configurer le modèle par défaut

Dans RunPod, définissez :

```bash
DEFAULT_VISION_MODEL=llama3.2-vision
```

## 📝 Exemples de prompts

### Description générale

```python
"Décris cette image en détail"
"Que vois-tu sur cette photo?"
"Fais une description complète de cette image"
```

### Questions spécifiques

```python
"Combien de personnes sont sur cette photo?"
"Quelle est la couleur dominante?"
"Y a-t-il des animaux dans cette image?"
"Quel temps fait-il sur cette photo?"
```

### OCR (lecture de texte)

```python
"Lis et transcris tout le texte visible dans cette image"
"Extrais le texte de ce document"
"Quelle est l'inscription sur le panneau?"
```

### Analyse technique

```python
"Explique ce diagramme de circuit électronique"
"Décris l'architecture montrée dans ce schéma"
"Analyse ce graphique et résume les tendances"
```

### Analyse créative/artistique

```python
"Analyse le style artistique de cette peinture"
"Décris la composition et l'utilisation des couleurs"
"Quelle émotion cette image évoque-t-elle?"
```

### Comparaison d'images

```python
payload = {
    "images": [image1_b64, image2_b64],
    "prompt": "Compare ces deux images et liste leurs différences"
}
```

## 💡 Bonnes pratiques

### Optimiser la température

- **0.1-0.3** : Descriptions factuelles, OCR, comptage
- **0.5-0.7** : Usage général équilibré
- **0.8-1.0** : Descriptions créatives, interprétations artistiques

### Taille des images

- **Résolution recommandée** : 512x512 à 1024x1024 pixels
- **Formats supportés** : JPEG, PNG, WebP, GIF
- **Taille maximale** : Environ 4-5 MB en base64

```python
# Redimensionner avant l'envoi (optionnel)
from PIL import Image

img = Image.open("large_image.jpg")
img.thumbnail((1024, 1024))
img.save("resized.jpg", quality=85)
```

### Gérer les timeouts

Pour les grosses images ou analyses complexes, augmentez le timeout :

```python
response = requests.post(url, json=payload, headers=headers, timeout=300)
```

### Économiser les tokens

```python
# Limiter la longueur de réponse
"max_tokens": 256  # Pour réponses courtes

# Prompt concis
"Liste les objets" au lieu de "Peux-tu me faire une liste détaillée..."
```

## 🔧 Tests et débogage

### Tester avec une image simple

```bash
# Image de test 1x1 pixel rouge (minimal)
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==" > test_red.txt

# Tester
./vision_client.py test_image.jpg "Quelle couleur?"
```

### Vérifier la configuration

```bash
# Vérifier que les variables sont définies
echo $RUNPOD_ENDPOINT_ID
echo $RUNPOD_TOKEN
echo $RUNPOD_API_KEY
```

### Déboguer les erreurs

```python
# Mode verbose
import logging
logging.basicConfig(level=logging.DEBUG)

# Vérifier la taille du base64
import base64
with open("image.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
    print(f"Taille base64: {len(b64)} caractères")
```

## ⚡ Optimisations

### Pré-télécharger le modèle

Dans `start.sh`, vous pouvez pré-charger le modèle de vision :

```bash
# Après le pull du modèle texte
if [ -n "$DEFAULT_VISION_MODEL" ]; then
    echo "Pulling vision model: $DEFAULT_VISION_MODEL"
    ollama pull "$DEFAULT_VISION_MODEL"
fi
```

### Batch processing

Pour analyser plusieurs images :

```python
images = ["img1.jpg", "img2.jpg", "img3.jpg"]

for img in images:
    result = analyze_image(img, "Décris brièvement")
    print(f"{img}: {result['output']['response']}\n")
```

### Cache des résultats

```python
import hashlib
import json

def get_cache_key(image_path, prompt):
    with open(image_path, "rb") as f:
        img_hash = hashlib.md5(f.read()).hexdigest()
    return f"{img_hash}_{prompt}"

# Utiliser un cache (Redis, fichier, etc.)
```

## 🐛 Problèmes courants

### "Model is not a vision model"

**Cause** : Le modèle spécifié n'est pas un modèle de vision

**Solution** : Utilisez un modèle de la liste : llama3.2-vision, llava, bakllava, moondream

### "Invalid base64 image data"

**Cause** : L'image n'est pas correctement encodée en base64

**Solution** :

```python
import base64

# Vérifier l'encodage
with open("image.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
    # Pas de \n, \r ou espaces
    b64 = b64.strip()
```

### "Out of memory"

**Cause** : Image trop grande ou GPU insuffisant

**Solution** :
- Réduire la résolution de l'image
- Utiliser un GPU avec plus de VRAM
- Utiliser un modèle plus petit (moondream)

### Timeout

**Cause** : Analyse trop longue

**Solution** :
- Réduire `max_tokens`
- Augmenter le timeout de requête
- Utiliser un GPU plus puissant

## 📚 Ressources

- [Ollama Vision Models](https://ollama.ai/library?sort=popular&q=vision)
- [LLaVA Documentation](https://llava-vl.github.io/)
- [API Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)

## 🎓 Exemples avancés

### Analyse de documents

```python
analyze_image("facture.pdf", 
    "Extrais les informations suivantes: numéro de facture, date, montant total")
```

### Détection d'anomalies

```python
analyze_image("piece_defaut.jpg",
    "Y a-t-il des défauts ou anomalies visibles sur cette pièce?")
```

### Aide à l'accessibility

```python
analyze_image("webpage_screenshot.png",
    "Décris cette page web pour une personne malvoyante")
```

---

**💡 Astuce** : Pour de meilleurs résultats, soyez spécifique dans vos prompts et utilisez des images de bonne qualité !

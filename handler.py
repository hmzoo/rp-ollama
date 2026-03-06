import runpod
import requests
import json
import os
import base64
from typing import Dict, Any, List

# Configuration via variables d'environnement
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:3b")
DEFAULT_VISION_MODEL = os.getenv("DEFAULT_VISION_MODEL", "llama3.2-vision")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))
API_KEY = os.getenv("RUNPOD_API_KEY", "")  # Clé API pour sécuriser l'endpoint
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Modèles de vision supportés
VISION_MODELS = [
    "llava", "llava:7b", "llava:13b", "llava:34b",
    "bakllava", "llama3.2-vision", "llama3.2-vision:11b",
    "moondream", "cogvlm"
]

def validate_api_key(inp: Dict[str, Any]) -> bool:
    """Valide la clé API si elle est configurée"""
    if not API_KEY:
        return True  # Pas de validation si pas de clé configurée
    
    provided_key = inp.get("api_key", "")
    return provided_key == API_KEY

def is_vision_model(model: str) -> bool:
    """Vérifie si le modèle est un modèle de vision"""
    return any(vm in model.lower() for vm in VISION_MODELS)

def validate_base64_image(image_data: str) -> bool:
    """Valide qu'une chaîne est bien une image base64"""
    try:
        # Retirer le préfixe data:image si présent
        if image_data.startswith('data:image'):
            image_data = image_data.split(',', 1)[1]
        
        # Vérifier que c'est du base64 valide
        base64.b64decode(image_data)
        return True
    except Exception:
        return False

def process_images(images: List[str]) -> List[str]:
    """
    Traite une liste d'images en format base64
    Supporte les formats :
    - Base64 pur
    - Data URI (data:image/png;base64,...)
    - URLs (télécharge et convertit en base64)
    """
    processed_images = []
    
    for img in images:
        # Si c'est une data URI, extraire le base64
        if img.startswith('data:image'):
            img = img.split(',', 1)[1]
        
        # Si c'est une URL, télécharger l'image
        elif img.startswith('http://') or img.startswith('https://'):
            try:
                response = requests.get(img, timeout=10)
                response.raise_for_status()
                img = base64.b64encode(response.content).decode('utf-8')
            except Exception as e:
                raise ValueError(f"Failed to download image from URL: {str(e)}")
        
        # Valider que c'est du base64 valide
        if not validate_base64_image(img):
            raise ValueError("Invalid base64 image data")
        
        processed_images.append(img)
    
    return processed_images

def handler(job):
    """
    Handler principal pour les requêtes Ollama (texte et vision)
    
    Format d'entrée pour texte:
    {
        "api_key": "votre_cle_api",  # Optionnel si RUNPOD_API_KEY n'est pas défini
        "model": "llama3.2:3b",      # Optionnel, utilise DEFAULT_MODEL si absent
        "prompt": "votre question",   # Requis
        "temperature": 0.7,           # Optionnel
        "max_tokens": 512             # Optionnel
    }
    
    Format d'entrée pour vision:
    {
        "api_key": "votre_cle_api",
        "model": "llama3.2-vision",   # Modèle de vision
        "prompt": "Décris cette image",
        "images": ["base64_image_data"] ou "base64_image_data",  # Image(s) en base64
        "temperature": 0.7,
        "max_tokens": 512
    }
    """
    try:
        inp = job["input"]
        
        # Validation de la clé API
        if not validate_api_key(inp):
            return {
                "error": "Invalid or missing API key",
                "status_code": 401
            }
        
        # Validation du prompt
        if "prompt" not in inp or not inp["prompt"]:
            return {
                "error": "Prompt is required",
                "status_code": 400
            }
        
        # Déterminer le modèle à utiliser
        model = inp.get("model")
        has_images = "images" in inp or "image" in inp
        
        # Si pas de modèle spécifié, choisir selon la présence d'images
        if not model:
            model = DEFAULT_VISION_MODEL if has_images else DEFAULT_MODEL
        
        # Construction de la requête Ollama
        ollama_req = {
            "model": model,
            "prompt": inp["prompt"],
            "stream": False,
            "options": {
                "temperature": inp.get("temperature", DEFAULT_TEMPERATURE),
                "num_predict": inp.get("max_tokens", DEFAULT_MAX_TOKENS)
            }
        }
        
        # Ajout d'options supplémentaires si fournies
        if "top_p" in inp:
            ollama_req["options"]["top_p"] = inp["top_p"]
        if "top_k" in inp:
            ollama_req["options"]["top_k"] = inp["top_k"]
        if "repeat_penalty" in inp:
            ollama_req["options"]["repeat_penalty"] = inp["repeat_penalty"]
        
        # Traitement des images pour les modèles de vision
        if has_images:
            # Vérifier que c'est un modèle de vision
            if not is_vision_model(model):
                return {
                    "error": f"Model '{model}' is not a vision model. Use one of: {', '.join(VISION_MODELS)}",
                    "status_code": 400
                }
            
            # Récupérer les images (supporte "image" ou "images")
            images = inp.get("images") or inp.get("image")
            
            # Normaliser en liste
            if isinstance(images, str):
                images = [images]
            elif not isinstance(images, list):
                return {
                    "error": "Images must be a string or list of base64-encoded images",
                    "status_code": 400
                }
            
            # Traiter les images
            try:
                ollama_req["images"] = process_images(images)
            except ValueError as e:
                return {
                    "error": str(e),
                    "status_code": 400
                }
        
        # Requête vers Ollama
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=ollama_req,
            timeout=300  # 5 minutes timeout
        )
        
        if resp.status_code == 200:
            result = resp.json()
            return {
                "response": result["response"],
                "model": model,
                "done": result.get("done", True),
                "context": result.get("context", []),
                "total_duration": result.get("total_duration"),
                "load_duration": result.get("load_duration"),
                "prompt_eval_count": result.get("prompt_eval_count"),
                "eval_count": result.get("eval_count"),
                "is_vision": has_images
            }
        else:
            return {
                "error": f"Ollama API error: {resp.text}",
                "status_code": resp.status_code
            }
            
    except requests.exceptions.Timeout:
        return {
            "error": "Request timeout - model took too long to respond",
            "status_code": 504
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Request error: {str(e)}",
            "status_code": 500
        }
    except KeyError as e:
        return {
            "error": f"Missing required field: {str(e)}",
            "status_code": 400
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "status_code": 500
        }

runpod.serverless.start({"handler": handler})

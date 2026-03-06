import runpod
import requests
import json
import os
from typing import Dict, Any

# Configuration via variables d'environnement
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:3b")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))
API_KEY = os.getenv("RUNPOD_API_KEY", "")  # Clé API pour sécuriser l'endpoint
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def validate_api_key(inp: Dict[str, Any]) -> bool:
    """Valide la clé API si elle est configurée"""
    if not API_KEY:
        return True  # Pas de validation si pas de clé configurée
    
    provided_key = inp.get("api_key", "")
    return provided_key == API_KEY

def handler(job):
    """
    Handler principal pour les requêtes Ollama
    
    Format d'entrée attendu:
    {
        "api_key": "votre_cle_api",  # Optionnel si RUNPOD_API_KEY n'est pas défini
        "model": "llama3.2:3b",      # Optionnel, utilise DEFAULT_MODEL si absent
        "prompt": "votre question",   # Requis
        "temperature": 0.7,           # Optionnel
        "max_tokens": 512             # Optionnel
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
        
        # Construction de la requête Ollama
        model = inp.get("model", DEFAULT_MODEL)
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
                "eval_count": result.get("eval_count")
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

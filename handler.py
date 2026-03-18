import runpod
import requests
import json
import os
import base64
import logging
import time
from typing import Dict, Any, List

# Configuration via variables d'environnement
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:3b")
DEFAULT_VISION_MODEL = os.getenv("DEFAULT_VISION_MODEL", "llama3.2-vision")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))
API_KEY = os.getenv("RUNPOD_API_KEY", "")  # Clé API pour sécuriser l'endpoint
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Configuration du logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_REQUEST_PREVIEW_CHARS = int(os.getenv("LOG_REQUEST_PREVIEW_CHARS", "180"))
LOG_RESPONSE_PREVIEW_CHARS = int(os.getenv("LOG_RESPONSE_PREVIEW_CHARS", "240"))
LOG_RAW_PAYLOAD = os.getenv("LOG_RAW_PAYLOAD", "false").lower() in ("1", "true", "yes")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("runpod-ollama-handler")

# Modèles de vision supportés (patterns pour détection depuis .env)
VISION_MODELS_DEFAULT = "llava,bakllava,llama3.2-vision,moondream,cogvlm,minicpm-v,qwen,qwen2-vl,qwen-vl,pixtral,internvl,molmo,video,vision"
VISION_MODELS = os.getenv("VISION_MODELS_PATTERNS", VISION_MODELS_DEFAULT).split(",")
VISION_MODELS = [vm.strip() for vm in VISION_MODELS]  # Nettoyer les espaces


def safe_preview(value: Any, max_len: int) -> str:
    """Construit une preview courte et sûre pour les logs."""
    text = "" if value is None else str(value)
    if len(text) <= max_len:
        return text
    return f"{text[:max_len]}... (truncated, len={len(text)})"


def get_request_id(job: Dict[str, Any]) -> str:
    """Récupère un identifiant de requête exploitable pour corréler les logs."""
    return str(
        job.get("id")
        or job.get("requestId")
        or job.get("request_id")
        or "unknown-request-id"
    )


def request_summary(inp: Dict[str, Any], resolved_model: str = "") -> Dict[str, Any]:
    """Résumé non sensible de la requête pour observabilité."""
    image_field = inp.get("images") if "images" in inp else inp.get("image")
    image_count = 0
    if isinstance(image_field, list):
        image_count = len(image_field)
    elif isinstance(image_field, str) and image_field:
        image_count = 1

    return {
        "model": resolved_model or inp.get("model", ""),
        "prompt_chars": len(inp.get("prompt", "") or ""),
        "prompt_preview": safe_preview(inp.get("prompt", ""), LOG_REQUEST_PREVIEW_CHARS),
        "has_system": bool(inp.get("system")),
        "temperature": inp.get("temperature", DEFAULT_TEMPERATURE),
        "max_tokens": inp.get("max_tokens", DEFAULT_MAX_TOKENS),
        "top_p": inp.get("top_p"),
        "top_k": inp.get("top_k"),
        "repeat_penalty": inp.get("repeat_penalty"),
        "has_images": "images" in inp or "image" in inp,
        "image_count": image_count,
        "api_key_provided": bool(inp.get("api_key")),
    }


def log_event(level: str, event: str, request_id: str, **fields: Any) -> None:
    """Journalise un événement au format JSON pour faciliter l'analyse."""
    payload = {
        "event": event,
        "request_id": request_id,
        **fields,
    }
    message = json.dumps(payload, ensure_ascii=False, default=str)
    if level == "debug":
        logger.debug(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.info(message)

def is_vision_model(model: str) -> bool:
    """
    Vérifie si le modèle est un modèle de vision.
    Détecte par patterns ou si le mot 'vision' est dans le nom.
    """
    model_lower = model.lower()
    # Vérifier les patterns connus
    if any(vm in model_lower for vm in VISION_MODELS):
        return True
    # Détection générique : si "vision" ou "vl" (vision-language) dans le nom
    if "vision" in model_lower or "-vl" in model_lower or "vl-" in model_lower:
        return True
    return False

def validate_api_key(inp: Dict[str, Any]) -> bool:
    """Valide la clé API si elle est configurée"""
    if not API_KEY:
        return True  # Pas de validation si pas de clé configurée
    
    provided_key = inp.get("api_key", "")
    return provided_key == API_KEY

def check_and_pull_model(model: str) -> Dict[str, Any]:
    """
    Vérifie si le modèle existe, sinon le télécharge automatiquement.
    Retourne un dict avec 'success' et optionnellement 'error'.
    """
    try:
        # Vérifier si le modèle existe déjà
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            # Vérifier avec et sans tag :latest
            model_base = model.split(':')[0]
            if model in model_names or f"{model_base}:latest" in model_names or any(m.startswith(model_base + ":") for m in model_names):
                return {"success": True, "message": f"Model {model} already available"}
        
        # Le modèle n'existe pas, le télécharger
        print(f"📥 Model {model} not found, pulling...")
        pull_resp = requests.post(
            f"{OLLAMA_HOST}/api/pull",
            json={"name": model, "stream": False},
            timeout=600  # 10 minutes pour le téléchargement
        )
        
        if pull_resp.status_code == 200:
            print(f"✅ Model {model} pulled successfully")
            return {"success": True, "message": f"Model {model} pulled successfully"}
        else:
            error_msg = f"Failed to pull model {model}: {pull_resp.text}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
            
    except requests.exceptions.Timeout:
        error_msg = f"Timeout while pulling model {model}"
        print(f"⏱️ {error_msg}")
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Error checking/pulling model {model}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

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
        "system": "You are a helpful assistant",  # Optionnel, system prompt
        "temperature": 0.7,           # Optionnel
        "max_tokens": 512             # Optionnel
    }
    
    Format d'entrée pour vision:
    {
        "api_key": "votre_cle_api",
        "model": "llama3.2-vision",   # Modèle de vision
        "prompt": "Décris cette image",
        "system": "You are an expert image analyst",  # Optionnel
        "images": ["base64_image_data"] ou "base64_image_data",  # Image(s) en base64
        "temperature": 0.7,
        "max_tokens": 512
    }
    """
    request_id = get_request_id(job)
    start_time = time.perf_counter()

    try:
        inp = job["input"]
        has_images = "images" in inp or "image" in inp

        log_event(
            "info",
            "request_received",
            request_id,
            job_keys=sorted(list(job.keys())),
            input_keys=sorted(list(inp.keys())),
            has_images=has_images,
            raw_input=inp if LOG_RAW_PAYLOAD else "disabled",
        )
        
        # Validation de la clé API
        if not validate_api_key(inp):
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_event(
                "warning",
                "request_rejected",
                request_id,
                reason="invalid_or_missing_api_key",
                elapsed_ms=elapsed_ms,
                request=request_summary(inp),
            )
            return {
                "error": "Invalid or missing API key",
                "status_code": 401
            }
        
        # Validation du prompt
        if "prompt" not in inp or not inp["prompt"]:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_event(
                "warning",
                "request_rejected",
                request_id,
                reason="missing_prompt",
                elapsed_ms=elapsed_ms,
            )
            return {
                "error": "Prompt is required",
                "status_code": 400
            }
        
        # Déterminer le modèle à utiliser
        model = inp.get("model")
        # Si pas de modèle spécifié, choisir selon la présence d'images
        if not model:
            model = DEFAULT_VISION_MODEL if has_images else DEFAULT_MODEL

        log_event(
            "info",
            "request_validated",
            request_id,
            request=request_summary(inp, resolved_model=model),
        )
        
        # Vérifier et télécharger le modèle si nécessaire
        pull_result = check_and_pull_model(model)
        if not pull_result["success"]:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_event(
                "error",
                "model_unavailable",
                request_id,
                model=model,
                error=pull_result.get("error", "unknown_error"),
                elapsed_ms=elapsed_ms,
            )
            return {
                "error": f"Model unavailable: {pull_result.get('error', 'Unknown error')}",
                "status_code": 503
            }
        
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
        
        # Ajout du system prompt si fourni
        if "system" in inp:
            ollama_req["system"] = inp["system"]
        
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
                log_event(
                    "info",
                    "images_processed",
                    request_id,
                    image_count=len(ollama_req["images"]),
                )
            except ValueError as e:
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                log_event(
                    "warning",
                    "request_rejected",
                    request_id,
                    reason="invalid_image_payload",
                    details=str(e),
                    elapsed_ms=elapsed_ms,
                )
                return {
                    "error": str(e),
                    "status_code": 400
                }
        
        # Requête vers Ollama
        log_event(
            "info",
            "ollama_request_started",
            request_id,
            model=model,
            has_images=has_images,
            timeout_seconds=300,
            ollama_host=OLLAMA_HOST,
        )
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=ollama_req,
            timeout=300  # 5 minutes timeout
        )
        
        if resp.status_code == 200:
            result = resp.json()
            response_text = result.get("response", "")
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_event(
                "info",
                "request_succeeded",
                request_id,
                model=model,
                elapsed_ms=elapsed_ms,
                prompt_eval_count=result.get("prompt_eval_count"),
                eval_count=result.get("eval_count"),
                total_duration_ns=result.get("total_duration"),
                load_duration_ns=result.get("load_duration"),
                response_chars=len(response_text),
                response_preview=safe_preview(response_text, LOG_RESPONSE_PREVIEW_CHARS),
            )
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
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_event(
                "error",
                "request_failed",
                request_id,
                model=model,
                status_code=resp.status_code,
                elapsed_ms=elapsed_ms,
                ollama_error_preview=safe_preview(resp.text, LOG_RESPONSE_PREVIEW_CHARS),
            )
            return {
                "error": f"Ollama API error: {resp.text}",
                "status_code": resp.status_code
            }
            
    except requests.exceptions.Timeout:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        log_event(
            "error",
            "request_failed",
            request_id,
            reason="timeout",
            elapsed_ms=elapsed_ms,
        )
        return {
            "error": "Request timeout - model took too long to respond",
            "status_code": 504
        }
    except requests.exceptions.RequestException as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        log_event(
            "error",
            "request_failed",
            request_id,
            reason="request_exception",
            details=str(e),
            elapsed_ms=elapsed_ms,
        )
        return {
            "error": f"Request error: {str(e)}",
            "status_code": 500
        }
    except KeyError as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        log_event(
            "warning",
            "request_rejected",
            request_id,
            reason="missing_required_field",
            details=str(e),
            elapsed_ms=elapsed_ms,
        )
        return {
            "error": f"Missing required field: {str(e)}",
            "status_code": 400
        }
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        log_event(
            "error",
            "request_failed",
            request_id,
            reason="unexpected_error",
            details=str(e),
            elapsed_ms=elapsed_ms,
        )
        return {
            "error": f"Unexpected error: {str(e)}",
            "status_code": 500
        }

runpod.serverless.start({"handler": handler})

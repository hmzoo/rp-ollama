#!/usr/bin/env python3
"""
Client pour tester l'analyse d'images avec les modèles de vision Ollama
"""

import requests
import os
import sys
import base64
from pathlib import Path

# Configuration
RUNPOD_ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "YOUR_ENDPOINT_ID")
RUNPOD_TOKEN = os.getenv("RUNPOD_TOKEN", "YOUR_RUNPOD_TOKEN")
API_KEY = os.getenv("RUNPOD_API_KEY", "your_secret_api_key")

def image_to_base64(image_path: str) -> str:
    """Convertit une image locale en base64"""
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def analyze_image(
    image_path: str,
    prompt: str,
    model: str = "llama3.2-vision",
    **kwargs
):
    """
    Analyse une image avec un modèle de vision
    
    Args:
        image_path: Chemin local de l'image ou URL
        prompt: Question ou instruction sur l'image
        model: Modèle de vision à utiliser
        **kwargs: Paramètres additionnels
    
    Returns:
        dict: La réponse du serveur
    """
    url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/runsync"
    
    # Convertir l'image en base64 si c'est un fichier local
    if os.path.isfile(image_path):
        print(f"📷 Chargement de l'image: {image_path}")
        image_data = image_to_base64(image_path)
    elif image_path.startswith('http://') or image_path.startswith('https://'):
        print(f"🌐 Utilisation de l'URL: {image_path}")
        image_data = image_path
    else:
        print(f"❌ Fichier introuvable: {image_path}")
        return {"error": "File not found"}
    
    payload = {
        "input": {
            "api_key": API_KEY,
            "prompt": prompt,
            "model": model,
            "images": [image_data],
            **kwargs
        }
    }
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"🤖 Modèle: {model}")
    print(f"💬 Prompt: {prompt}\n")
    print("⏳ Analyse en cours...\n")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        if "output" in result:
            output = result["output"]
            if "response" in output:
                print("="*60)
                print("✅ ANALYSE DE L'IMAGE")
                print("="*60)
                print(output["response"])
                print("\n" + "="*60)
                print(f"📊 Statistiques:")
                print(f"   Modèle: {output.get('model', 'N/A')}")
                print(f"   Mode vision: {output.get('is_vision', False)}")
                print(f"   Tokens prompt: {output.get('prompt_eval_count', 'N/A')}")
                print(f"   Tokens générés: {output.get('eval_count', 'N/A')}")
                if output.get('total_duration'):
                    duration_sec = output['total_duration'] / 1_000_000_000
                    print(f"   Durée: {duration_sec:.2f}s")
                print("="*60)
                return output
            elif "error" in output:
                print(f"❌ Erreur: {output['error']}")
                return output
        else:
            print(f"⚠️  Réponse inattendue: {result}")
            return result
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - L'analyse prend trop de temps")
        return {"error": "Timeout"}
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return {"error": str(e)}

def main():
    """Fonction principale"""
    
    # Vérifier la configuration
    if RUNPOD_ENDPOINT_ID == "YOUR_ENDPOINT_ID":
        print("⚠️  Attention: RUNPOD_ENDPOINT_ID n'est pas configuré")
        print("Définissez la variable d'environnement RUNPOD_ENDPOINT_ID")
        sys.exit(1)
        
    if RUNPOD_TOKEN == "YOUR_RUNPOD_TOKEN":
        print("⚠️  Attention: RUNPOD_TOKEN n'est pas configuré")
        print("Définissez la variable d'environnement RUNPOD_TOKEN")
        sys.exit(1)
    
    # Usage
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <chemin_image> [prompt]")
        print(f"  {sys.argv[0]} <url_image> [prompt]")
        print("\nExemples:")
        print(f"  {sys.argv[0]} photo.jpg \"Que vois-tu sur cette image?\"")
        print(f"  {sys.argv[0]} https://example.com/image.png \"Décris cette image\"")
        print("\nModèles de vision supportés:")
        print("  - llama3.2-vision (par défaut)")
        print("  - llava:7b, llava:13b, llava:34b")
        print("  - bakllava")
        print("  - moondream")
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Décris cette image en détail"
    
    # Analyser l'image
    analyze_image(
        image_path=image_path,
        prompt=prompt,
        model="llama3.2-vision",
        temperature=0.3,
        max_tokens=512
    )

if __name__ == "__main__":
    main()

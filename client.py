#!/usr/bin/env python3
"""
Client exemple pour tester l'endpoint RunPod Ollama
"""

import requests
import os
import sys
import json

# Configuration
RUNPOD_ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "YOUR_ENDPOINT_ID")
RUNPOD_TOKEN = os.getenv("RUNPOD_TOKEN", "YOUR_RUNPOD_TOKEN")
API_KEY = os.getenv("RUNPOD_API_KEY", "your_secret_api_key")

def query_ollama(prompt: str, model: str = "llama3.2:3b", **kwargs):
    """
    Interroge l'endpoint RunPod Ollama
    
    Args:
        prompt: Le prompt à envoyer
        model: Le modèle à utiliser
        **kwargs: Paramètres additionnels (temperature, max_tokens, etc.)
    
    Returns:
        dict: La réponse du serveur
    """
    url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/runsync"
    
    payload = {
        "input": {
            "api_key": API_KEY,
            "prompt": prompt,
            "model": model,
            **kwargs
        }
    }
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Envoi de la requête à {model}...")
    print(f"📝 Prompt: {prompt}\n")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        if "output" in result:
            output = result["output"]
            if "response" in output:
                print("✅ Réponse reçue:\n")
                print(output["response"])
                print("\n" + "="*50)
                print(f"📊 Statistiques:")
                print(f"   Modèle: {output.get('model', 'N/A')}")
                print(f"   Tokens prompt: {output.get('prompt_eval_count', 'N/A')}")
                print(f"   Tokens générés: {output.get('eval_count', 'N/A')}")
                if output.get('total_duration'):
                    duration_sec = output['total_duration'] / 1_000_000_000
                    print(f"   Durée: {duration_sec:.2f}s")
                return output
            elif "error" in output:
                print(f"❌ Erreur: {output['error']}")
                return output
        else:
            print(f"⚠️  Réponse inattendue: {result}")
            return result
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - Le modèle met trop de temps à répondre")
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
    
    # Exemples de requêtes
    examples = [
        {
            "prompt": "Explique en une phrase ce qu'est l'intelligence artificielle",
            "temperature": 0.7,
            "max_tokens": 100
        },
        {
            "prompt": "Écris un haiku sur le printemps",
            "temperature": 0.9,
            "max_tokens": 50
        }
    ]
    
    # Si un prompt est fourni en argument, l'utiliser
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        query_ollama(prompt, temperature=0.7, max_tokens=512)
    else:
        # Sinon, exécuter les exemples
        print("🔧 Mode exemple - utilisez './client.py \"votre prompt\"' pour un prompt personnalisé\n")
        for i, example in enumerate(examples, 1):
            print(f"\n{'='*50}")
            print(f"Exemple {i}/{len(examples)}")
            print('='*50 + "\n")
            query_ollama(**example)
            if i < len(examples):
                input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()

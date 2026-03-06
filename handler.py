import runpod
import requests
import json
import os

def handler(job):
    inp = job["input"]
    
    # Ollama local API
    ollama_req = {
        "model": inp.get("model", "llama3.2:3b"),  # ton défaut
        "prompt": inp["prompt"],
        "stream": False,
        "options": {
            "temperature": inp.get("temperature", 0.7),
            "num_predict": inp.get("max_tokens", 512)
        }
    }
    
    resp = requests.post("http://localhost:11434/api/generate", json=ollama_req)
    
    if resp.status_code == 200:
        return {"response": resp.json()["response"]}
    else:
        return {"error": resp.text, "status_code": resp.status_code}

runpod.serverless.start({"handler": handler})

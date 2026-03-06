#!/bin/bash

echo "Starting Ollama server..."
ollama serve &

# Attendre que Ollama soit prêt
echo "Waiting for Ollama to be ready..."
until curl -s http://localhost:11434/api/tags >/dev/null 2>&1; do
    sleep 1
done

echo "Ollama is ready!"

# Charger le modèle par défaut si spécifié
if [ -n "$DEFAULT_MODEL" ]; then
    echo "Pulling default model: $DEFAULT_MODEL"
    ollama pull "$DEFAULT_MODEL"
fi

echo "Starting RunPod handler..."
python3 -u handler.py

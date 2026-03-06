#!/bin/bash
set -e

echo "🚀 Starting Ollama server..."

# Démarrer Ollama en arrière-plan
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

echo "⏳ Waiting for Ollama to be ready..."
MAX_RETRIES=60
RETRY_COUNT=0

while ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -gt $MAX_RETRIES ]; then
        echo "❌ ERROR: Ollama failed to start after $MAX_RETRIES attempts"
        echo "📋 Ollama logs:"
        cat /tmp/ollama.log || echo "No logs available"
        echo "🔍 Process check:"
        ps aux | grep ollama || echo "No ollama process found"
        echo "🔍 Ollama location:"
        which ollama || echo "Ollama not in PATH"
        exit 1
    fi
    if [ $((RETRY_COUNT % 10)) -eq 0 ]; then
        echo "   Still waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    fi
    sleep 1
done

echo "✅ Ollama is ready!"

# Charger le modèle par défaut si spécifié
if [ -n "$DEFAULT_MODEL" ]; then
    echo "📥 Pulling default text model: $DEFAULT_MODEL"
    ollama pull "$DEFAULT_MODEL" || echo "⚠️  Warning: Failed to pull $DEFAULT_MODEL"
fi

# Charger le modèle de vision par défaut si spécifié et différent
if [ -n "$DEFAULT_VISION_MODEL" ] && [ "$DEFAULT_VISION_MODEL" != "$DEFAULT_MODEL" ]; then
    echo "📥 Pulling default vision model: $DEFAULT_VISION_MODEL"
    ollama pull "$DEFAULT_VISION_MODEL" || echo "⚠️  Warning: Failed to pull $DEFAULT_VISION_MODEL"
fi

echo "🐍 Starting RunPod handler..."
python3.11 -u handler.py


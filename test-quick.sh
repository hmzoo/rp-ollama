#!/bin/bash
# Script de test synchrone simple pour RunPod

set -e

# Charger les variables depuis .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❌ Fichier .env non trouvé"
    exit 1
fi

if [ -z "$RUNPOD_TOKEN" ]; then
    echo "❌ RUNPOD_TOKEN manquant - ajoutez-le dans .env"
    exit 1
fi

# Modifier l'URL pour utiliser /runsync si nécessaire
SYNC_URL="${RUNPOD_API_URL%/run}/runsync"

echo "🚀 Test synchrone rapide"
echo ""

# Payload avec ou sans api_key
if [ -n "$RUNPOD_API_KEY" ]; then
    PAYLOAD="{\"input\":{\"api_key\":\"$RUNPOD_API_KEY\",\"model\":\"${1:-tinyllama}\",\"prompt\":\"${2:-Hello, how are you?}\",\"temperature\":0.7,\"max_tokens\":100}}"
else
    PAYLOAD="{\"input\":{\"model\":\"${1:-tinyllama}\",\"prompt\":\"${2:-Hello, how are you?}\",\"temperature\":0.7,\"max_tokens\":100}}"
fi

curl -s -X POST "$SYNC_URL" \
    -H "Authorization: Bearer $RUNPOD_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" | {
    if command -v jq &> /dev/null; then
        jq -C '.'
    else
        python3 -m json.tool 2>/dev/null || cat
    fi
}

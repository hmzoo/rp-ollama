#!/bin/bash
# Script de test pour RunPod avec chargement automatique du .env

set -e

# Charger les variables depuis .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Variables chargées depuis .env"
else
    echo "❌ Fichier .env non trouvé"
    exit 1
fi

# Vérifier que les variables nécessaires sont définies
if [ -z "$RUNPOD_API_URL" ]; then
    echo "❌ RUNPOD_API_URL non défini dans .env"
    exit 1
fi

if [ -z "$RUNPOD_TOKEN" ]; then
    echo "❌ RUNPOD_TOKEN non défini dans .env"
    echo "📍 Trouvez-le sur: https://www.runpod.io/console/user/settings"
    exit 1
fi

echo "🚀 Test du endpoint RunPod"
echo "📍 URL: $RUNPOD_API_URL"
echo ""

# Déterminer si c'est /run ou /runsync
if [[ "$RUNPOD_API_URL" == *"/run" ]]; then
    MODE="async"
else
    MODE="sync"
fi

# Préparer le payload
PROMPT="${1:-Explain what is Ollama in 2 sentences.}"
MODEL="${2:-$DEFAULT_MODEL}"

echo "💬 Prompt: $PROMPT"
echo "🤖 Model: $MODEL"
echo "⚙️  Mode: $MODE"
echo ""

# Construire la requête JSON
if [ -n "$RUNPOD_API_KEY" ]; then
    JSON_PAYLOAD=$(cat <<EOF
{
  "input": {
    "api_key": "$RUNPOD_API_KEY",
    "model": "$MODEL",
    "prompt": "$PROMPT",
    "temperature": ${DEFAULT_TEMPERATURE:-0.7},
    "max_tokens": ${DEFAULT_MAX_TOKENS:-512}
  }
}
EOF
)
else
    JSON_PAYLOAD=$(cat <<EOF
{
  "input": {
    "model": "$MODEL",
    "prompt": "$PROMPT",
    "temperature": ${DEFAULT_TEMPERATURE:-0.7},
    "max_tokens": ${DEFAULT_MAX_TOKENS:-512}
  }
}
EOF
)
fi

echo "📤 Envoi de la requête..."
echo ""

# Faire la requête
RESPONSE=$(curl -s -X POST "$RUNPOD_API_URL" \
    -H "Authorization: Bearer $RUNPOD_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

echo "📥 Réponse:"
if command -v jq &> /dev/null; then
    echo "$RESPONSE" | jq -C '.'
else
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
fi

echo ""

# Si mode async, proposer de vérifier le statut
if [[ "$MODE" == "async" ]] && echo "$RESPONSE" | grep -q '"id"'; then
    JOB_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    STATUS_URL="${RUNPOD_API_URL%/run}/status/$JOB_ID"
    
    echo "ℹ️  Job ID: $JOB_ID"
    echo "📍 Status URL: $STATUS_URL"
    echo ""
    echo "Pour vérifier le statut:"
    echo "  curl -s \"$STATUS_URL\""
fi

#!/bin/bash
# Tester la liste des modèles disponibles sur RunPod

set -e

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❌ Fichier .env non trouvé"
    exit 1
fi

if [ -z "$RUNPOD_TOKEN" ]; then
    echo "❌ RUNPOD_TOKEN manquant"
    exit 1
fi

echo "📋 Test: Lister les modèles disponibles"
echo ""

# Requête pour lister les modèles
curl -s -X POST "$RUNPOD_API_URL" \
    -H "Authorization: Bearer $RUNPOD_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "input": {
        "list_models": true
      }
    }' | jq -C '.'

echo ""
echo "💡 Si le job échoue, c'est normal - essayez:"
echo "   1. Configurez DEFAULT_MODEL dans RunPod.io"
echo "   2. Ou attendez le téléchargement du modèle"

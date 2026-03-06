#!/bin/bash
# Test d'analyse d'images avec modèle vision

# Configuration du modèle vision
VISION_MODEL="${VISION_MODEL:-lukey03/qwen3.5-9b-abliterated-vision}"

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

IMAGE_PATH="${1}"
PROMPT="${2:-What do you see in this image?}"

if [ -z "$IMAGE_PATH" ]; then
    echo "Usage: $0 <image_path> [prompt]"
    echo ""
    echo "Modèle par défaut: $VISION_MODEL"
    echo "Pour changer le modèle: VISION_MODEL=autre-modele $0 <image_path>"
    echo ""
    echo "Modèles vision supportés (détection automatique) :"
    echo "  - llava, bakllava"
    echo "  - llama3.2-vision"
    echo "  - minicpm-v, qwen2-vl, pixtral"
    echo "  - Ou tout modèle avec 'vision' ou 'vl' dans le nom"
    echo ""
    echo "Exemples:"
    echo "  $0 /path/to/image.jpg"
    echo "  $0 /path/to/image.png 'Describe this image in detail'"
    echo "  VISION_MODEL=llava $0 /path/to/image.jpg"
    echo "  VISION_MODEL=minicpm-v:latest $0 /path/to/image.jpg"
    exit 1
fi

if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ Image non trouvée: $IMAGE_PATH"
    exit 1
fi

echo "🖼️  Test d'analyse d'image"
echo "📍 Image: $IMAGE_PATH"
echo "🤖 Modèle: $VISION_MODEL"
echo "💬 Prompt: $PROMPT"
echo ""

# Convertir l'image en base64
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_PATH")

# Utiliser /runsync pour réponse immédiate
SYNC_URL="${RUNPOD_API_URL%/run}/runsync"

echo "📤 Envoi de l'image au modèle vision..."
echo ""

# Payload avec ou sans api_key
if [ -n "$RUNPOD_API_KEY" ]; then
    PAYLOAD="{\"input\":{\"api_key\":\"$RUNPOD_API_KEY\",\"model\":\"$VISION_MODEL\",\"prompt\":\"$PROMPT\",\"images\":[\"$IMAGE_BASE64\"],\"temperature\":0.7,\"max_tokens\":300}}"
else
    PAYLOAD="{\"input\":{\"model\":\"$VISION_MODEL\",\"prompt\":\"$PROMPT\",\"images\":[\"$IMAGE_BASE64\"],\"temperature\":0.7,\"max_tokens\":300}}"
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

#!/bin/bash

echo "🐳 Test de l'image Docker en local"
echo "===================================="
echo ""

# Variables
IMAGE_NAME="rp-ollama:test"
CONTAINER_NAME="rp-ollama-test"

# Nettoyer les anciens conteneurs
echo "🧹 Nettoyage des anciens conteneurs..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Builder l'image
echo ""
echo "🔨 Build de l'image Docker..."
docker build -t $IMAGE_NAME . || {
    echo "❌ Erreur lors du build"
    exit 1
}

echo ""
echo "✅ Build réussi!"
echo ""
echo "🚀 Lancement du conteneur..."
echo "   (Ceci peut prendre quelques minutes pour télécharger le modèle)"
echo ""

# Lancer le conteneur
docker run --name $CONTAINER_NAME \
    -e DEFAULT_MODEL=llama3.2:3b \
    -e RUNPOD_API_KEY=test_key_local \
    --gpus all \
    -p 11434:11434 \
    $IMAGE_NAME &

CONTAINER_ID=$!

echo "📋 Conteneur lancé (ID: $CONTAINER_ID)"
echo ""
echo "Attendez que Ollama soit prêt..."
echo "Vous pouvez suivre les logs dans un autre terminal avec:"
echo "   docker logs -f $CONTAINER_NAME"
echo ""
echo "Pour tester manuellement:"
echo "   1. Attendre que les logs montrent 'Starting RunPod handler...'"
echo "   2. Tester avec: curl http://localhost:11434/api/tags"
echo ""
echo "Pour arrêter:"
echo "   docker stop $CONTAINER_NAME"
echo ""
echo "Logs en direct:"
echo "==============="

docker logs -f $CONTAINER_NAME

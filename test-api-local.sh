#!/bin/bash

echo "🧪 Test de l'API Ollama locale"
echo "=============================="
echo ""

# Vérifier que le conteneur tourne
if ! docker ps | grep -q "rp-ollama-test"; then
    echo "❌ Le conteneur rp-ollama-test ne tourne pas"
    echo "Lancez d'abord: ./test-docker-local.sh"
    exit 1
fi

echo "✅ Conteneur détecté"
echo ""

# Test 1: API Ollama
echo "Test 1: Vérifier l'API Ollama..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ API Ollama répond"
    echo "   Modèles disponibles:"
    curl -s http://localhost:11434/api/tags | python3 -m json.tool 2>/dev/null || echo "   (impossible de parser JSON)"
else
    echo "❌ API Ollama ne répond pas"
    echo "Attendez quelques secondes et réessayez"
    exit 1
fi

echo ""
echo "Test 2: Génération de texte..."

# Test 2: Génération simple
RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llama3.2:3b",
        "prompt": "Dis bonjour en une phrase",
        "stream": false
    }')

if echo "$RESPONSE" | grep -q "response"; then
    echo "✅ Génération réussie!"
    echo "   Réponse: $(echo $RESPONSE | python3 -c 'import sys, json; print(json.load(sys.stdin)["response"][:100])' 2>/dev/null || echo 'voir ci-dessous')"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "❌ Échec de la génération"
    echo "Réponse: $RESPONSE"
fi

echo ""
echo "📊 Statistiques du conteneur:"
docker stats --no-stream rp-ollama-test

echo ""
echo "✅ Tests terminés!"
echo ""
echo "Pour voir les logs: docker logs rp-ollama-test"
echo "Pour arrêter: docker stop rp-ollama-test"
echo "Pour supprimer: docker rm rp-ollama-test"

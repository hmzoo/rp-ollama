#!/bin/bash
# Script de diagnostic pour l'endpoint RunPod

set -e

echo "🔍 Diagnostic de l'endpoint RunPod"
echo "=================================="
echo ""

# Charger les variables depuis .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Variables chargées depuis .env"
else
    echo "❌ Fichier .env non trouvé"
    exit 1
fi

echo ""
echo "📍 Configuration:"
echo "   URL: $RUNPOD_API_URL"
echo "   API Key: ${RUNPOD_API_KEY:0:20}..."
echo ""

# Extraire l'endpoint ID
ENDPOINT_ID=$(echo "$RUNPOD_API_URL" | grep -oP 'v2/\K[^/]+' || echo "unknown")
echo "🆔 Endpoint ID: $ENDPOINT_ID"
echo ""

# Test 1: Mode async simple
echo "📤 Test 1: Mode async (/run)"
echo "   Envoi d'une requête async..."

RESPONSE=$(timeout 5 curl -s -X POST "$RUNPOD_API_URL" \
    -H "Content-Type: application/json" \
    -d "{
      \"input\": {
        \"api_key\": \"$RUNPOD_API_KEY\",
        \"model\": \"tinyllama\",
        \"prompt\": \"Test\",
        \"max_tokens\": 10
      }
    }" 2>&1) || RESPONSE="TIMEOUT"

if [ "$RESPONSE" = "TIMEOUT" ]; then
    echo "   ⚠️  Timeout après 5 secondes"
    echo "   💡 Votre endpoint est peut-être en pause (cold start)"
else
    echo "   Réponse reçue:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "   $RESPONSE"
fi

echo ""

# Test 2: Health check (si disponible)
echo "📤 Test 2: Health check"
HEALTH_URL="${RUNPOD_API_URL%/*}/health"
HEALTH=$(timeout 3 curl -s "$HEALTH_URL" 2>&1) || HEALTH="TIMEOUT"

if [ "$HEALTH" = "TIMEOUT" ]; then
    echo "   ⚠️  Timeout"
else
    echo "   $HEALTH"
fi

echo ""
echo "📚 Diagnostic terminé"
echo ""
echo "💡 Solutions possibles:"
echo "   1. Votre endpoint est en pause → Attendez le cold start (30-60s)"
echo "   2. Vérifiez sur RunPod.io que l'endpoint est actif"
echo "   3. Mode serverless: Les workers s'arrêtent après inactivité"
echo "   4. Utilisez le mode async + vérification du statut"
echo ""
echo "📖 Pour tester async + statut:"
echo "   ./test-runpod.sh \"Your prompt here\""

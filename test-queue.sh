#!/bin/bash
# Script pour monitorer la queue et les jobs RunPod

set -e

# Charger les variables depuis .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❌ Fichier .env non trouvé"
    exit 1
fi

# Vérifier RUNPOD_TOKEN
if [ -z "$RUNPOD_TOKEN" ]; then
    echo "❌ RUNPOD_TOKEN manquant dans .env"
    echo "💡 Ajoutez: RUNPOD_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    echo "📍 Trouvez-le sur: https://www.runpod.io/console/user/settings"
    exit 1
fi

ENDPOINT_ID=$(echo "$RUNPOD_API_URL" | grep -oP 'v2/\K[^/]+' || echo "unknown")

echo "🔍 Monitoring RunPod Queue"
echo "=========================="
echo ""
echo "🆔 Endpoint ID: $ENDPOINT_ID"
echo ""

# Fonction pour afficher les détails avec code HTTP
test_request() {
    local url="$1"
    local method="${2:-GET}"
    local data="$3"
    
    echo "📡 Testing: $method $url"
    
    if [ -n "$data" ]; then
        RESPONSE=$(curl -w "\n---\nHTTP_CODE:%{http_code}\nTIME:%{time_total}s" \
            -s -X "$method" "$url" \
            -H "Authorization: Bearer $RUNPOD_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    else
        RESPONSE=$(curl -w "\n---\nHTTP_CODE:%{http_code}\nTIME:%{time_total}s" \
            -s -X "$method" "$url" \
            -H "Authorization: Bearer $RUNPOD_TOKEN" 2>&1)
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
    TIME=$(echo "$RESPONSE" | grep "TIME:" | cut -d: -f2)
    BODY=$(echo "$RESPONSE" | sed '/^---$/,$d')
    
    echo "   Code HTTP: $HTTP_CODE"
    echo "   Temps: $TIME"
    
    if [ -n "$BODY" ] && [ "$BODY" != "" ]; then
        echo "   Body:"
        echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    else
        echo "   Body: (vide)"
    fi
    echo ""
}

# Test 1: Soumettre un job
echo "📤 Test 1: Soumettre un job async"

# Construire le payload (avec ou sans api_key selon si RUNPOD_API_KEY est défini)
if [ -n "$RUNPOD_API_KEY" ]; then
    JOB_PAYLOAD="{
  \"input\": {
    \"api_key\": \"$RUNPOD_API_KEY\",
    \"model\": \"tinyllama\",
    \"prompt\": \"Hi, test message $(date +%s)\",
    \"max_tokens\": 10
  }
}"
else
    JOB_PAYLOAD="{
  \"input\": {
    \"model\": \"tinyllama\",
    \"prompt\": \"Hi, test message $(date +%s)\",
    \"max_tokens\": 10
  }
}"
fi

test_request "$RUNPOD_API_URL" "POST" "$JOB_PAYLOAD"

# Extraire le job ID de la dernière réponse
JOB_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$JOB_ID" ] && [ "$JOB_ID" != "" ]; then
    echo "✅ Job créé: $JOB_ID"
    echo ""
    
    # Test 2: Vérifier le statut
    echo "📤 Test 2: Vérifier le statut du job"
    STATUS_URL="${RUNPOD_API_URL%/run}/status/$JOB_ID"
    test_request "$STATUS_URL" "GET"
    
    # Test 3: Attendre et re-vérifier
    echo "⏳ Attente de 5 secondes..."
    sleep 5
    echo ""
    echo "📤 Test 3: Re-vérifier le statut"
    test_request "$STATUS_URL" "GET"
else
    echo "❌ Pas de job ID reçu - vérifiez les logs ci-dessus"
fi

echo ""
echo "📊 Résumé"
echo "========="
echo ""
echo "💡 Vérifications à faire sur RunPod.io:"
echo "   1. Allez sur: https://www.runpod.io/console/serverless"
echo "   2. Ouvrez votre endpoint: $ENDPOINT_ID"
echo "   3. Regardez l'onglet 'Logs' pour voir les requêtes"
echo "   4. Vérifiez l'onglet 'Requests' pour la queue"
echo "   5. Assurez-vous qu'il y a au moins 1 worker actif"
echo ""
echo "🔍 Si vous ne voyez pas de requêtes:"
echo "   - L'endpoint est peut-être désactivé"
echo "   - Le worker n'a pas démarré (cold start peut prendre 30-60s)"
echo "   - Erreur dans la configuration (API key, modèle, etc.)"

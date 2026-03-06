# Scripts de Test RunPod

Collection de scripts pour tester facilement votre endpoint RunPod Ollama.

## 📋 Prérequis

1. Fichier `.env` configuré avec vos credentials :
   ```bash
   RUNPOD_API_KEY=rpa_...
   RUNPOD_API_URL=https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run
   DEFAULT_MODEL=tinyllama
   ```

2. Outils nécessaires :
   - `curl` (installé par défaut)
   - `python3` (pour formater JSON)
   - `jq` (optionnel, meilleur formatage)

## 🚀 Scripts Disponibles

### 1. Test Rapide Synchrone
```bash
./test-quick.sh [model] [prompt]
```

**Exemples** :
```bash
./test-quick.sh                                    # Utilise tinyllama + prompt par défaut
./test-quick.sh tinyllama "What is AI?"           # Prompt personnalisé
./test-quick.sh llama3.2:3b "Explain Docker"      # Autre modèle
```

⚠️ **Note** : Le mode sync peut timeout sur cold start. Utilisez le mode async si ça arrive.

---

### 2. Test Complet (Async + Sync)
```bash
./test-runpod.sh [prompt] [model]
```

**Exemples** :
```bash
./test-runpod.sh                                   # Prompt par défaut
./test-runpod.sh "Explain Kubernetes"              # Prompt personnalisé
./test-runpod.sh "What is Python?" llama3.2:3b     # Avec modèle spécifique
```

**Fonctionnalités** :
- ✅ Détecte automatiquement mode async/sync
- ✅ Affiche le job ID pour suivi
- ✅ Propose la commande pour vérifier le statut

---

### 3. Test Vision (Analyse d'Images)
```bash
./test-vision.sh <image_path> [prompt]
```

**Exemples** :
```bash
./test-vision.sh photo.jpg                         # Analyse basique
./test-vision.sh image.png "What colors do you see?"  # Prompt personnalisé
./test-vision.sh ~/Pictures/diagram.jpg "Explain this diagram"
```

**Formats supportés** : JPG, PNG, GIF, WebP

---

### 4. Diagnostic
```bash
./test-diagnostic.sh
```

Effectue plusieurs tests pour diagnostiquer les problèmes de connexion.

**Utiliser quand** :
- ❌ Les autres scripts timeout
- ❌ Pas de réponse de l'endpoint
- ❓ Vous ne savez pas si l'endpoint fonctionne

---

## 🔧 Configuration du .env

Créez un fichier `.env` à la racine du projet :

```bash
# Votre clé API RunPod (depuis votre dashboard)
RUNPOD_API_KEY=rpa_XXXXXXXXXXXXXXXXXXXXXXXX

# URL de votre endpoint (format: /run pour async, /runsync pour sync)
RUNPOD_API_URL=https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run

# Modèles par défaut
DEFAULT_MODEL=tinyllama
DEFAULT_VISION_MODEL=llama3.2-vision

# Paramètres
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=512
```

## 📊 Modes de Fonctionnement

### Mode Synchrone (`/runsync`)
✅ **Avantages** :
- Réponse immédiate dans la même requête
- Plus simple à utiliser

❌ **Inconvénients** :
- Timeout possible sur cold start (30-60s)
- Limite de temps de réponse

### Mode Asynchrone (`/run`)
✅ **Avantages** :
- Pas de timeout
- Idéal pour cold start
- Supporte les longues générations

❌ **Inconvénients** :
- Nécessite 2 requêtes (envoi + vérification statut)

**Vérifier le statut d'un job async** :
```bash
curl -s "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status/JOB_ID" | python3 -m json.tool
```

## 🐛 Résolution de Problèmes

### Timeout après 5-10 secondes
**Cause** : Cold start (endpoint en pause)

**Solution** : 
1. Utilisez le mode async (`./test-runpod.sh`)
2. Ou attendez 30-60s et réessayez

### "Connection refused"
**Cause** : URL incorrecte ou endpoint désactivé

**Solutions** :
- Vérifiez `RUNPOD_API_URL` dans `.env`
- Vérifiez que l'endpoint est actif sur RunPod.io
- Testez avec `./test-diagnostic.sh`

### "Unauthorized" ou erreur 401
**Cause** : API key incorrecte

**Solutions** :
- Vérifiez `RUNPOD_API_KEY` dans `.env`
- Régénérez votre API key sur RunPod.io

### "Model not found"
**Cause** : Modèle pas téléchargé sur l'endpoint

**Solutions** :
- Utilisez `tinyllama` (petit et rapide)
- Ou configurez `DEFAULT_MODEL` dans les env vars RunPod
- Attendez que le modèle se télécharge au premier appel

## 💡 Bonnes Pratiques

1. **Pour les tests** : Utilisez `tinyllama` (petit et rapide)
2. **Pour la production** : Utilisez `llama3.2:3b` (meilleure qualité)
3. **Pour la vision** : Assurez-vous que le modèle vision est installé
4. **Cold starts** : Les endpoints serverless s'arrêtent après inactivité (normal)
5. **Coûts** : Le mode serverless facture à l'utilisation, pensez à arrêter si inutilisé

## 📝 Exemples Complets

### Test basique
```bash
# 1. Configuration
echo 'RUNPOD_API_KEY=rpa_...' > .env
echo 'RUNPOD_API_URL=https://api.runpod.ai/v2/xxx/run' >> .env

# 2. Test rapide
./test-quick.sh tinyllama "Hello!"

# 3. Si timeout, utilisez async
./test-runpod.sh "Hello!"
```

### Test avec vision
```bash
# Télécharger une image de test
curl -o test.jpg https://picsum.photos/400/300

# Analyser l'image
./test-vision.sh test.jpg "Describe this image"
```

### Curl direct (sans scripts)
```bash
# Charger les variables
source .env

# Requête async
curl -X POST "$RUNPOD_API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "api_key": "'"$RUNPOD_API_KEY"'",
      "model": "tinyllama",
      "prompt": "Hello!",
      "max_tokens": 50
    }
  }'

# Si vous obtenez un job ID, vérifiez le statut
curl "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status/JOB_ID"
```

## 🔗 Ressources

- [Documentation RunPod](https://docs.runpod.io/)
- [Documentation Ollama](https://ollama.ai/docs)
- [Repository GitHub](https://github.com/hmzoo/rp-ollama)

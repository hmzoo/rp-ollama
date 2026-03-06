# 🚀 Guide de déploiement sur RunPod

## Prérequis

- Un compte RunPod ([https://runpod.io](https://runpod.io))
- Un dépôt Git (GitHub, GitLab, etc.) avec ce code
- Docker Hub ou un registre Docker (optionnel)

## Option 1 : Déploiement via GitHub (Recommandé)

### 1. Préparer votre dépôt

```bash
git add .
git commit -m "Configuration serverless Ollama"
git push origin main
```

### 2. Créer un endpoint sur RunPod

1. Connectez-vous à [RunPod.io](https://runpod.io)
2. Allez dans **Serverless** > **+ New Endpoint**
3. Configurez :
   - **Name** : `ollama-endpoint` (ou votre choix)
   - **Select a Template** : Custom
   
### 3. Configurer l'image Docker

Deux options :

#### A. Build automatique depuis GitHub

- **Container Image** : Sélectionnez "Build from GitHub"
- **Repository** : `https://github.com/hmzoo/rp-ollama.git`
- **Branch** : `main`
- **Dockerfile Path** : `Dockerfile`

#### B. Image Docker pré-buildée

```bash
# Builder et pusher votre image
docker build -t votre-username/rp-ollama:latest .
docker push votre-username/rp-ollama:latest
```

Puis dans RunPod :
- **Container Image** : `votre-username/rp-ollama:latest`

### 4. Configurer les variables d'environnement

Dans la section **Environment Variables**, ajoutez :

```
DEFAULT_MODEL=llama3.2:3b
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=512
RUNPOD_API_KEY=votre_cle_secrete_aleatoire
```

**Important** : Générez une clé API sécurisée :
```bash
openssl rand -hex 32
```

### 5. Configurer les ressources

- **GPU** : Selon votre modèle
  - `llama3.2:3b` → 1x RTX 3090 (24GB) minimum
  - `llama3:8b` → 1x RTX 4090 ou A6000
  - Modèles plus gros → A100 ou plus
  
- **Container Disk** : 20GB minimum (50GB recommandé pour les gros modèles)
- **Workers** : 
  - **Min** : 0 (scale to zero pour économiser)
  - **Max** : 3-5 selon vos besoins
- **Idle Timeout** : 5 secondes
- **Execution Timeout** : 300 secondes (5 minutes)

### 6. Déployer

1. Cliquez sur **Deploy**
2. Attendez que le build soit terminé (5-10 minutes)
3. L'endpoint sera actif quand le statut est "Ready"

### 7. Tester votre endpoint

Récupérez votre **Endpoint ID** et votre **API Key** dans l'interface RunPod.

```bash
# Configurer les variables d'environnement
export RUNPOD_ENDPOINT_ID="votre-endpoint-id"
export RUNPOD_TOKEN="votre-runpod-api-token"
export RUNPOD_API_KEY="votre_cle_secrete"

# Tester avec le client
./client.py "Explique l'intelligence artificielle"
```

Ou avec curl :

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_RUNPOD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "api_key": "votre_cle_secrete",
      "prompt": "Bonjour, comment ça va?"
    }
  }'
```

## Option 2 : Déploiement manuel via Docker Hub

### 1. Builder et pusher l'image

```bash
# Se connecter à Docker Hub
docker login

# Builder l'image
docker build -t votre-username/rp-ollama:latest .

# Pusher l'image
docker push votre-username/rp-ollama:latest
```

### 2. Créer l'endpoint RunPod

Suivez les étapes 2-7 de l'Option 1, en utilisant votre image Docker Hub.

## 📊 Monitoring

### Vérifier les logs

1. Dans l'interface RunPod, cliquez sur votre endpoint
2. Allez dans **Logs**
3. Recherchez :
   - ✅ `Starting Ollama server...`
   - ✅ `Ollama is ready!`
   - ✅ `Pulling default model: llama3.2:3b`
   - ✅ `Starting RunPod handler...`

### Métriques importantes

- **Requests** : Nombre de requêtes traitées
- **Errors** : Taux d'erreur
- **Duration** : Temps de réponse moyen
- **Cold Start** : Temps de démarrage d'un nouveau worker

## 💰 Optimisation des coûts

### Scale to Zero

Configurez **Min Workers = 0** pour que les workers s'arrêtent automatiquement quand ils ne sont pas utilisés.

**Attention** : Le premier appel après un arrêt prendra plus de temps (cold start : 30-60 secondes).

### Choisir le bon GPU

| Modèle | GPU recommandé | Coût approximatif |
|--------|----------------|-------------------|
| llama3.2:3b | RTX 3090 (24GB) | $0.0006/sec |
| llama3:8b | RTX 4090 (24GB) | $0.0008/sec |
| llama3:70b | A100 (80GB) | $0.002/sec |

### Optimiser max_tokens

Réduisez `DEFAULT_MAX_TOKENS` si vous n'avez pas besoin de longues réponses. Moins de tokens = moins de temps de calcul.

## 🐛 Dépannage

### Le build échoue

- Vérifiez que le Dockerfile est à la racine
- Vérifiez que tous les fichiers sont présents (handler.py, start.sh, requirements.txt)
- Consultez les logs de build dans RunPod

### "Ollama API error: Connection refused"

- Ollama n'a pas démarré correctement
- Vérifiez les logs : `ollama serve` doit être lancé
- Le script `start.sh` doit être exécutable

### "Model not found"

- Le modèle n'a pas été téléchargé
- Vérifiez que `DEFAULT_MODEL` existe sur [Ollama Library](https://ollama.ai/library)
- Augmentez le timeout pour les gros modèles

### "Out of memory"

- Le modèle est trop gros pour le GPU choisi
- Choisissez un GPU avec plus de VRAM
- Ou utilisez un modèle plus petit

### Performances lentes

- Le GPU est sous-dimensionné
- Trop de requêtes simultanées → augmentez Max Workers
- Cold start → considérez Min Workers = 1

## 🔐 Sécurité en production

### ✅ À faire

- ✅ Définir `RUNPOD_API_KEY` avec une clé forte et aléatoire
- ✅ Utiliser HTTPS uniquement
- ✅ Monitorer les logs pour détecter les abus
- ✅ Limiter les rate limits via l'interface RunPod
- ✅ Restreindre les IPs autorisées si possible

### ❌ À éviter

- ❌ Laisser l'endpoint sans authentification
- ❌ Commiter `.env` dans Git
- ❌ Partager votre API key publiquement
- ❌ Utiliser des clés faibles type "123456"

## 📚 Ressources

- [Documentation RunPod](https://docs.runpod.io/)
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Modèles Ollama](https://ollama.ai/library)
- [RunPod Discord](https://discord.gg/runpod)

## 🆘 Support

En cas de problème :
1. Consultez les logs RunPod
2. Vérifiez cette documentation
3. Ouvrez une issue sur GitHub
4. Contact : [votre email ou discord]

---

**Astuce** : Gardez une copie de votre `RUNPOD_API_KEY` dans un gestionnaire de mots de passe sécurisé !

# Configuration du Volume Persistant RunPod

## � Auto-téléchargement des Modèles

Les modèles sont **téléchargés automatiquement** à la première requête qui les utilise :
- ✅ Aucune pré-configuration nécessaire
- ✅ Utilisez n'importe quel modèle de [Ollama Library](https://ollama.ai/library)
- 💾 Modèles persistés automatiquement sur le volume

**Exemple** : 
```bash
# Première requête avec "tinyllama" → téléchargement auto (~30s)
# Requêtes suivantes avec "tinyllama" → utilise le cache (~2s)
```

## 📦 Stockage des Modèles

Un **volume persistant** évite le re-téléchargement des modèles entre les redémarrages de workers.

### Configuration Automatique

Les modèles Ollama sont automatiquement stockés dans `/runpod-volume/models` grâce à :

1. **Variable d'environnement** (Dockerfile) :
   ```bash
   ENV OLLAMA_MODELS=/runpod-volume/models
   ```

2. **Création automatique du répertoire** (start.sh) :
   ```bash
   mkdir -p /runpod-volume/models
   ```

### Avantages

✅ **Pas de re-téléchargement** : Les modèles sont téléchargés une seule fois  
✅ **Démarrage rapide** : Le conteneur démarre en quelques secondes au lieu de plusieurs minutes  
✅ **Économie de bande passante** : Réduit les coûts de transfert  
✅ **Multi-modèles** : Vous pouvez pré-charger plusieurs modèles

### Structure du Volume

```
/runpod-volume/
└── models/
    ├── manifests/
    │   └── registry.ollama.ai/
    │       └── library/
    │           ├── llama3.2/
    │           ├── tinyllama/
    │           └── llama3.2-vision/
    └── blobs/
        ├── sha256-abc123...
        ├── sha256-def456...
        └── ...
```

### Configuration RunPod

1. **Créer un Network Volume** dans RunPod :
   - Taille recommandée : **50 GB minimum** (modèles + données)
   - Région : Même région que votre endpoint

2. **Attacher le volume à votre endpoint** :
   - Container Disk : 20 GB (système + code)
   - Network Volume : `/runpod-volume` (modèles persistants)

3. **Variables d'environnement** (optionnelles) :
   ```bash
   RUNPOD_API_KEY=your_secret_key  # Sécurité (optionnel)
   DEFAULT_MODEL=llama3.2:3b  # Model par défaut si non spécifié dans requête
   DEFAULT_VISION_MODEL=llama3.2-vision  # Model vision par défaut
   ```

### Pré-charger des Modèles (OPTIONNEL)

Les modèles sont maintenant **auto-téléchargés à la demande**. 

Si vous souhaitez quand même pré-charger des modèles au démarrage pour éviter l'attente à la première requête, configurez :

```bash
# Dans l'environnement RunPod
DEFAULT_MODEL=llama3.2:3b
DEFAULT_VISION_MODEL=llama3.2-vision
```

**Note** : Sans ces variables, les modèles seront téléchargés automatiquement lors de la première utilisation.

### Vérifier les Modèles Disponibles

Via l'API Ollama :
```bash
curl http://localhost:11434/api/tags
```

Ou dans le volume :
```bash
ls -lh /runpod-volume/models/manifests/registry.ollama.ai/library/
```

### Tailles des Modèles Courants

| Modèle | Taille | Usage |
|--------|--------|-------|
| `tinyllama` | 637 MB | Tests rapides |
| `llama3.2:1b` | 1.3 GB | Léger et performant |
| `llama3.2:3b` | 2.0 GB | Bon équilibre qualité/vitesse |
| `llama3.2-vision` | 7.9 GB | Analyse d'images |
| `llava` | 4.7 GB | Vision alternative |
| `llama3.1:8b` | 4.7 GB | Haute qualité texte |

### Migration depuis un Volume Existant

Si vous avez déjà des modèles Ollama ailleurs :

```bash
# Copier depuis ~/.ollama/models vers le volume
cp -r ~/.ollama/models/* /runpod-volume/models/
```

### Nettoyage

Pour libérer de l'espace :

```bash
# Supprimer un modèle spécifique
ollama rm tinyllama

# Nettoyer les blobs non utilisés
ollama prune
```

### Dépannage

**Problème : Modèles non persistés**
- Vérifiez que `/runpod-volume` est bien monté : `ls /runpod-volume`
- Vérifiez la variable : `echo $OLLAMA_MODELS`

**Problème : Espace disque insuffisant**
- Augmentez la taille du Network Volume dans RunPod
- Supprimez les modèles inutilisés avec `ollama rm`

**Problème : Modèles corrompus**
- Supprimez le répertoire : `rm -rf /runpod-volume/models/*`
- Relancez le conteneur pour re-télécharger

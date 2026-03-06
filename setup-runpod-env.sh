#!/bin/bash
# Configuration rapide des variables d'environnement RunPod

cat << 'EOF'
🔧 Configuration RunPod - Variables d'Environnement
====================================================

Pour que votre endpoint fonctionne, configurez ces variables sur RunPod.io :

1. Allez sur: https://www.runpod.io/console/serverless
2. Cliquez sur votre endpoint
3. Settings → Environment Variables
4. Ajoutez ces variables :

┌─────────────────────────────────────────────────────────────┐
│ Variable                  │ Valeur recommandée              │
├───────────────────────────┼─────────────────────────────────┤
│ DEFAULT_MODEL             │ tinyllama (rapide, 637 MB)      │
│                           │ OU llama3.2:3b (qualité, 2 GB)  │
├───────────────────────────┼─────────────────────────────────┤
│ DEFAULT_TEMPERATURE       │ 0.7                             │
├───────────────────────────┼─────────────────────────────────┤
│ DEFAULT_MAX_TOKENS        │ 512                             │
├───────────────────────────┼─────────────────────────────────┤
│ OLLAMA_MODELS             │ /runpod-volume/models           │
│ (si volume persistant)    │                                 │
└───────────────────────────┴─────────────────────────────────┘

⚠️  IMPORTANT: DEFAULT_MODEL est OBLIGATOIRE pour télécharger le modèle

5. Sauvegardez et redémarrez les workers

📝 Optionnel (sécurité) :
┌───────────────────────────┬─────────────────────────────────┐
│ RUNPOD_API_KEY            │ Votre clé secrète personnelle   │
│                           │ (pour sécuriser le handler)     │
└───────────────────────────┴─────────────────────────────────┘

⏱️  Temps de démarrage après configuration:
- Premier lancement: 30-90s (téléchargement du modèle)
- Lancements suivants: ~8s (si volume persistant configuré)

✅ Une fois configuré, retestez avec:
   ./test-quick.sh tinyllama "Hello!"

EOF

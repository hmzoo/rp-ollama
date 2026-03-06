#!/bin/bash

# Script de test local pour vérifier la configuration avant le déploiement

echo "🔍 Vérification de la configuration RunPod Ollama"
echo "=================================================="
echo ""

# Vérifier que les fichiers nécessaires existent
echo "📁 Vérification des fichiers..."

required_files=("handler.py" "Dockerfile" "requirements.txt" "start.sh" ".env.example")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file manquant"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo ""
    echo "❌ Fichiers manquants: ${missing_files[*]}"
    exit 1
fi

echo ""
echo "📦 Vérification de Docker..."

if ! command -v docker &> /dev/null; then
    echo "  ❌ Docker n'est pas installé"
    exit 1
fi

echo "  ✅ Docker est installé"

echo ""
echo "🔧 Vérification du Dockerfile..."

if docker build -t rp-ollama-test . --no-cache > /tmp/docker-build.log 2>&1; then
    echo "  ✅ Le Dockerfile est valide et l'image se build correctement"
else
    echo "  ❌ Erreur lors du build Docker"
    echo ""
    tail -n 20 /tmp/docker-build.log
    exit 1
fi

echo ""
echo "📝 Vérification du handler.py..."

if python3 -m py_compile handler.py 2>/dev/null; then
    echo "  ✅ handler.py a une syntaxe Python valide"
else
    echo "  ❌ Erreur de syntaxe dans handler.py"
    python3 -m py_compile handler.py
    exit 1
fi

echo ""
echo "🔐 Vérification de la configuration de sécurité..."

if [ -f ".env" ]; then
    echo "  ⚠️  Fichier .env détecté"
    echo "     Assurez-vous qu'il n'est PAS commité dans Git!"
    
    if git ls-files --error-unmatch .env 2>/dev/null; then
        echo "  ❌ ATTENTION: .env est tracké par Git! Utilisez 'git rm --cached .env'"
    else
        echo "  ✅ .env n'est pas tracké par Git"
    fi
else
    echo "  ℹ️  Pas de fichier .env (optionnel pour les tests locaux)"
    echo "     Copiez .env.example vers .env si besoin"
fi

echo ""
echo "📋 Structure du projet:"
tree -L 1 -a 2>/dev/null || ls -la

echo ""
echo "✨ Résumé"
echo "========"
echo "✅ Tous les fichiers requis sont présents"
echo "✅ Le Dockerfile build correctement"
echo "✅ La syntaxe Python est valide"
echo ""
echo "🚀 Prêt pour le déploiement sur RunPod!"
echo ""
echo "Prochaines étapes:"
echo "1. Commitez vos changements: git add . && git commit -m 'Configure serverless'"
echo "2. Poussez sur GitHub: git push"
echo "3. Suivez le guide DEPLOYMENT.md pour déployer sur RunPod"
echo ""
echo "💡 Astuce: N'oubliez pas de configurer RUNPOD_API_KEY sur RunPod!"

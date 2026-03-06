# 🔑 Configuration des Clés RunPod

Il y a **2 types de clés** à configurer :

## 1️⃣ RUNPOD_TOKEN (Authentification API RunPod)

**Rôle** : Authentifier vos requêtes vers l'API RunPod
**Où** : Header `Authorization: Bearer RUNPOD_TOKEN`
**Trouver** : 
1. Allez sur https://www.runpod.io/console/user/settings
2. Section "API Keys"
3. Créez une clé ou copiez une existante
4. Format : `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

## 2️⃣ RUNPOD_API_KEY (Authentification Handler)

**Rôle** : Authentifier les requêtes traitées PAR votre handler
**Où** : Dans le body JSON `input.api_key`
**Définir** : Vous choisissez cette valeur (n'importe quel secret)
**Format** : N'importe quelle chaîne (ex: `rpa_...`)

---

## 📝 Configuration du .env

Ajoutez ces lignes à votre `.env` :

```bash
# === Authentification RunPod API ===
# Token pour s'authentifier à l'API RunPod (obligatoire)
# Trouvez-le sur: https://www.runpod.io/console/user/settings
RUNPOD_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# === Authentification Handler (optionnel) ===  
# Clé API pour sécuriser votre handler
# Si définie, les clients doivent envoyer cette clé dans input.api_key
RUNPOD_API_KEY=rpa_YOUR_SECRET_KEY_HERE

# === URL de l'Endpoint ===
# Format: https://api.runpod.ai/v2/ENDPOINT_ID/run
RUNPOD_API_URL=https://api.runpod.ai/v2/c4a4jgqnpc1lq2/run
```

---

## ✅ Vérification

Après avoir ajouté `RUNPOD_TOKEN`, testez :

```bash
./test-queue.sh
```

Vous devriez voir :
- ✅ Code HTTP: 200 (au lieu de 401)
- ✅ Job créé avec un ID
- ✅ Les requêtes apparaissent dans la queue RunPod

---

## 🔒 Sécurité

⚠️ **Ne commitez JAMAIS le `.env`** avec vos vraies clés !

Le fichier `.gitignore` contient déjà `.env` pour vous protéger.

Utilisez `.env.example` comme template sans vraies valeurs.

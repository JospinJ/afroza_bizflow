# Déploiement demo — collègues

Guide pour partager le chatbot Agent IA + panneau RAG avec l’équipe.

---

## Ce que voient vos collègues

| Zone | Contenu |
|------|---------|
| **Gauche** | Tous les `knowledge_items` Supabase (base RAG) |
| **Centre** | Chat client (comme WhatsApp) |
| **Droite** | Intent, confiance, items RAG injectés, texte du contexte LLM |

URL demo : `/a/salon-aicha`

---

## Option 1 — Réseau local (même bureau / VPN)

**Machine qui héberge :**

```powershell
# API
cd services\api
.\start.ps1

# Frontend (autre terminal)
cd apps\web
npm install
npm run dev -- -H 0.0.0.0
```

**Collègues :** `http://IP-DE-VOTRE-PC:3000/a/salon-aicha`

Dans `apps/web/.env.local` :
```env
NEXT_PUBLIC_API_URL=http://IP-DE-VOTRE-PC:8001
```

Pare-feu Windows : autoriser ports **3000** et **8001**.

---

## Option 2 — ngrok (partage internet, 10 min)

```powershell
# Terminal 1 — API déjà lancée sur 8001
ngrok http 8001

# Terminal 2 — frontend
cd apps\web
# .env.local → NEXT_PUBLIC_API_URL=https://xxxx.ngrok-free.app (URL API)
npm run dev
ngrok http 3000
```

Envoyer aux collègues l’URL ngrok du **frontend** (port 3000).

---

## Option 3 — Production (recommandé équipe distante)

### Frontend → [Vercel](https://vercel.com)

1. New Project → repo GitHub
2. **Root Directory** : `apps/web`
3. Environment variable :
   ```
   NEXT_PUBLIC_API_URL=https://afroza-api.onrender.com
   ```
4. Deploy

### API → [Render](https://render.com) (gratuit)

1. New Web Service → repo
2. **Root** : `services/api`
3. **Build** : `pip install -r requirements.txt`
4. **Start** : `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Variables :
   - `GROQ_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `PAYMENT_MODE=simulated`

6. Mettre à jour `NEXT_PUBLIC_API_URL` sur Vercel avec l’URL Render.

CORS est déjà ouvert (`allow_origins=["*"]`) dans `main.py`.

---

## Vérifications avant demo

```powershell
curl http://127.0.0.1:8001/health
# → {"status":"ok","supabase":true}

curl http://127.0.0.1:8001/api/agents/business/salon-aicha
# → knowledge_items avec Braids, Tissage, etc.
```

---

## Endpoints API utilisés par le front

| Méthode | Route | Rôle |
|---------|-------|------|
| GET | `/health` | Statut API + Supabase |
| GET | `/api/agents/business/{slug}` | Profil PME + base RAG complète |
| GET | `/api/agents/business/{slug}/rag-preview?intent=` | Simuler filtre RAG |
| POST | `/api/agents/chat` | Conversation |

---

## Sécurité (demo interne)

- Ne pas committer `.env` (clés Groq / Supabase)
- Rotation des clés Groq : `GROQ_API_KEY=key1,key2,key3`
- Pour prod publique : restreindre CORS + rate limiting

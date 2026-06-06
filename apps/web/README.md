# Demo web — Afroza BizFlow Agent IA

Interface Next.js pour montrer le chatbot Salon Aïcha + visualisation RAG Supabase.

## Lancer en local

**Terminal 1 — API**
```powershell
cd services\api
.\start.ps1
```

**Terminal 2 — Frontend**
```powershell
cd apps\web
copy .env.local.example .env.local
npm install
npm run dev
```

Ouvrir : **http://localhost:3000/a/salon-aicha**

## Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | URL FastAPI (défaut `http://127.0.0.1:8001`) |

## Déploiement pour collègues

### Option A — Local + ngrok (rapide)

1. Lancer API + frontend en local
2. `ngrok http 3000` → partager l’URL HTTPS
3. Mettre `NEXT_PUBLIC_API_URL` sur l’URL ngrok de l’API (port 8001) ou proxy

### Option B — Vercel (front) + Render/Railway (API)

**Frontend Vercel**
1. Importer le repo, root directory : `apps/web`
2. Variable : `NEXT_PUBLIC_API_URL=https://votre-api.onrender.com`
3. Deploy

**API Render / Railway**
1. Root : `services/api`
2. Start : `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Variables d’env : `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`

Voir [DEPLOIEMENT_DEMO.md](../../DEPLOIEMENT_DEMO.md) pour le guide complet.

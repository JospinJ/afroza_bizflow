# Afroza BizFlow — Lancement du projet

Projet actuel : **API Agent IA** (FastAPI). Le frontend Next.js n'est pas encore scaffoldé.

---

## Prérequis

| Outil | Version | Lien |
|-------|---------|------|
| Python | 3.11+ (vous avez 3.12) | [python.org](https://www.python.org/) |
| Clé Groq | obligatoire pour le chat | [console.groq.com](https://console.groq.com/) |
| Supabase | optionnel (phase 2) | [supabase.com](https://supabase.com/) |

---

## Méthode 1 — Script automatique (Windows)

```powershell
cd c:\Users\user\Desktop\AFROZAEDITOR\afroza_bizflow\services\api
.\start.ps1
```

Au premier lancement, le script crée `.env` depuis `.env.example`. **Éditez `.env`** et ajoutez votre clé :

```env
GROQ_API_KEY=gsk_votre_cle_ici
PAYMENT_MODE=simulated
```

Relancez `.\start.ps1`.

---

## Méthode 2 — Commandes manuelles

```powershell
cd c:\Users\user\Desktop\AFROZAEDITOR\afroza_bizflow\services\api

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

copy .env.example .env
# Editez .env → GROQ_API_KEY=...

uvicorn main:app --reload --port 8000
```

---

## Vérifier que ça tourne

| URL | Résultat |
|-----|----------|
| http://localhost:8000/health | `{"status":"ok","module":"agent_ia"}` |
| http://localhost:8000/docs | Interface Swagger (test interactif) |

---

## Tester l'agent Salon Aïcha

**Via Swagger** : ouvrir http://localhost:8000/docs → `POST /api/agents/chat` → Try it out :

```json
{
  "business_slug": "salon-aicha",
  "channel": "web",
  "message": "Bonjour, c'est combien les braids demain ?"
}
```

**Via PowerShell** :

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/agents/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"business_slug":"salon-aicha","message":"Bonjour, prix des braids ?"}'
```

---

## Erreurs fréquentes

| Erreur | Solution |
|--------|----------|
| `GROQ_API_KEY manquant` | Renseigner la clé dans `services/api/.env` |
| `Activate.ps1` bloqué | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Port 8000 occupé | `uvicorn main:app --reload --port 8001` |
| `python` introuvable | Utiliser `py -3.12` à la place |

---

## Supabase (optionnel — persistance données)

1. Créer un projet sur [supabase.com](https://supabase.com/)
2. SQL Editor → coller le contenu de `supabase/migrations/001_agent_core.sql` → Run
3. Copier URL + service role key dans `.env` :

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

*(L'orchestrator utilise encore les données demo en mémoire — branchement Supabase = prochaine étape.)*

---

## Structure du projet

```
afroza_bizflow/
├── services/api/          ← API Agent IA (à lancer ici)
│   ├── main.py
│   ├── start.ps1
│   ├── .env               ← vos clés (à créer)
│   └── agents/            ← classifier, RAG, orchestrator
├── supabase/migrations/   ← schéma SQL
├── PROCEDURE_AGENT_IA.md
├── PLAN_PROTOTYPE.md
└── RESUME_TECHNIQUE_NEXBIZ.md
```

---

## Prochaine étape après lancement

1. Tester 5–10 messages dans Swagger
2. Créer un eval set intents (`eval/intent_test_set.json`)
3. Brancher Supabase (voir `PROCEDURE_AGENT_IA.md` Phase 1)

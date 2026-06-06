# Agent IA — Démarrage rapide

## 1. Prérequis

- Python 3.11+
- Clé API [Groq](https://console.groq.com/)

## 2. Installation

```bash
cd services/api
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # puis renseigner GROQ_API_KEY
```

## 3. Lancer l'API

```bash
uvicorn main:app --reload --port 8000
```

## 4. Tester l'agent (Salon Aïcha demo)

```bash
curl -X POST http://localhost:8000/api/agents/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"business_slug\":\"salon-aicha\",\"message\":\"Bonjour, prix des braids demain ?\"}"
```

## 5. Prochaines étapes (ordre Data/IA)

1. Exécuter `supabase/migrations/001_agent_core.sql`
2. Brancher `orchestrator.py` sur Supabase (remplacer `_DEMO_BUSINESS`)
3. Construire eval set 100 messages → mesurer intent accuracy
4. Implémenter B3 (`qualification.py`) et B4 (`appointments.py`)
5. Connecter frontend `/a/[slug]` → POST `/api/agents/chat`

Voir [PROCEDURE_AGENT_IA.md](../../PROCEDURE_AGENT_IA.md) pour la procédure complète.

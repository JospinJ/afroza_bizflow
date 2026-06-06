"""Execute les migrations SQL sur Supabase (PostgreSQL direct)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT.parents[1] / "supabase" / "migrations"

load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))


def _split_sql(sql: str) -> list[str]:
    lines = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue
        lines.append(line)
    body = "\n".join(lines)
    parts = [p.strip() for p in body.split(";")]
    return [p for p in parts if p]


def _connect(password: str, ref: str):
    import psycopg2

    attempts = [
        {
            "host": os.getenv("SUPABASE_DB_POOLER_HOST", "aws-1-eu-central-1.pooler.supabase.com"),
            "port": 5432,
            "user": f"postgres.{ref}",
        },
        {
            "host": "aws-0-eu-central-1.pooler.supabase.com",
            "port": 5432,
            "user": f"postgres.{ref}",
        },
        {
            "host": os.getenv("SUPABASE_DB_HOST", f"db.{ref}.supabase.co"),
            "port": 5432,
            "user": "postgres",
        },
    ]
    last_err = None
    for cfg in attempts:
        try:
            print(f"Connexion -> {cfg['host']}:{cfg['port']}")
            conn = psycopg2.connect(
                host=cfg["host"],
                port=cfg["port"],
                dbname="postgres",
                user=cfg["user"],
                password=password,
                sslmode="require",
            )
            conn.autocommit = True
            return conn
        except Exception as e:
            last_err = e
            print(f"Echec: {e}")
    raise last_err


def main() -> None:
    password = os.getenv("SUPABASE_DB_PASSWORD", "").strip()
    if not password:
        print("ERREUR: ajoutez SUPABASE_DB_PASSWORD dans .env")
        sys.exit(1)

    try:
        import psycopg2  # noqa: F401
    except ImportError:
        print("pip install psycopg2-binary")
        sys.exit(1)

    ref = os.getenv("SUPABASE_PROJECT_ID", "gdnuveguhlpaohkyvpcp").strip()
    conn = _connect(password, ref)

    with conn:
        with conn.cursor() as cur:
            for sql_file in sorted(MIGRATIONS.glob("*.sql")):
                sql = sql_file.read_text(encoding="utf-8")
                statements = _split_sql(sql)
                print(f"Fichier: {sql_file.name} ({len(statements)} requetes)")
                for stmt in statements:
                    cur.execute(stmt)

    conn.close()
    print("SQL termine avec succes.")


if __name__ == "__main__":
    main()

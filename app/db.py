import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv(Path(__file__).parent.parent / ".env")

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "pgdb.icmc.usp.br"),
    "dbname":   os.environ.get("DB_NAME",     "scc541_g09_db"),
    "user":     os.environ.get("DB_USER",     "scc541_g09"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "port":     int(os.environ.get("DB_PORT", 5432)),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def query(sql, params=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def execute(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()

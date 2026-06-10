import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "host":     "pgdb.icmc.usp.br",
    "dbname":   "scc541_g09_db",
    "user":     "scc541_g09",
    "password": "REDACTED",
    "port":     5432,
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

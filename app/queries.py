import hashlib

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

# ── AUTENTICAÇÃO ──────────────────────────────────────────────────────────────

SQL_LOGIN = """
    SELECT userid, login, tipo, id_original
    FROM USERS
    WHERE login = %s AND password = %s
"""

SQL_INSERT_LOG = "INSERT INTO USERS_LOG (userid, tipo_acao) VALUES (%s, %s)"

# ── DASHBOARD ADMIN ───────────────────────────────────────────────────────────

SQL_ADMIN_TOTAIS = """
    SELECT
        (SELECT COUNT(*) FROM drivers)      AS total_pilotos,
        (SELECT COUNT(*) FROM constructors) AS total_escuderias,
        (SELECT COUNT(*) FROM seasons)      AS total_temporadas
"""

SQL_ADMIN_CORRIDAS_RECENTES = """
    SELECT
        rc.race_name                        AS corrida,
        ci.name                             AS circuito,
        rc.race_date                        AS data,
        rc.race_time                        AS horario,
        COALESCE(SUM(res.laps), 0)          AS total_voltas
    FROM races rc
    JOIN seasons s   ON s.id  = rc.season_id
    JOIN circuits ci ON ci.id = rc.circuit_id
    LEFT JOIN results res ON res.race_id = rc.id
    WHERE s.year = (SELECT MAX(year) FROM seasons)
    GROUP BY rc.id, rc.race_name, ci.name, rc.race_date, rc.race_time
    ORDER BY rc.race_date
"""

SQL_ADMIN_STANDINGS_ESCUDERIAS = """
    SELECT
        c.name        AS escuderia,
        SUM(r.points) AS total_pontos
    FROM results r
    JOIN constructors c  ON c.id  = r.constructor_id
    JOIN races        rc ON rc.id = r.race_id
    JOIN seasons      s  ON s.id  = rc.season_id
    WHERE s.year = (SELECT MAX(year) FROM seasons)
    GROUP BY c.id, c.name
    ORDER BY total_pontos DESC
"""

SQL_ADMIN_STANDINGS_PILOTOS = """
    SELECT
        d.given_name || ' ' || d.family_name AS piloto,
        SUM(r.points)                        AS total_pontos
    FROM results r
    JOIN drivers d  ON d.id  = r.driver_id
    JOIN races   rc ON rc.id = r.race_id
    JOIN seasons s  ON s.id  = rc.season_id
    WHERE s.year = (SELECT MAX(year) FROM seasons)
    GROUP BY d.id, d.given_name, d.family_name
    ORDER BY total_pontos DESC
"""

# ── DASHBOARD ESCUDERIA ───────────────────────────────────────────────────────

SQL_ESCUDERIA_INFO = """
    SELECT
        c.name                                         AS nome,
        fn_vitorias_escuderia(c.id)                    AS vitorias,
        fn_pilotos_escuderia(c.id)                     AS total_pilotos,
        (fn_anos_escuderia(c.id)).primeiro_ano         AS primeiro_ano,
        (fn_anos_escuderia(c.id)).ultimo_ano           AS ultimo_ano
    FROM constructors c
    WHERE c.id = %s
"""

# ── DASHBOARD PILOTO ──────────────────────────────────────────────────────────

SQL_PILOTO_INFO = """
    SELECT
        d.given_name || ' ' || d.family_name           AS nome_completo,
        (fn_anos_piloto(d.id)).primeiro_ano            AS primeiro_ano,
        (fn_anos_piloto(d.id)).ultimo_ano              AS ultimo_ano,
        (
            SELECT c.name
            FROM results r2
            JOIN races rc2 ON rc2.id = r2.race_id
            JOIN seasons s2 ON s2.id = rc2.season_id
            JOIN constructors c ON c.id = r2.constructor_id
            WHERE r2.driver_id = d.id
            ORDER BY s2.year DESC
            LIMIT 1
        ) AS escuderia_atual
    FROM drivers d
    WHERE d.id = %s
"""

SQL_PILOTO_DESEMPENHO = "SELECT * FROM fn_desempenho_piloto(%s)"

# ── RELATÓRIO 1 (Admin): resultados por status ────────────────────────────────

SQL_R1 = """
    SELECT
        st.status AS "Status",
        COUNT(*)  AS "Quantidade"
    FROM results r
    JOIN status st ON st.id = r.status_id
    GROUP BY st.status
    ORDER BY COUNT(*) DESC
"""

# ── RELATÓRIO 2 (Admin): cidades BR + aeroportos dentro de 100km ──────────────
# earthdistance não disponível — usa fórmula de Haversine em SQL puro

SQL_R2 = """
    SELECT
        ci_ref.name   AS "Cidade",
        a.iata_code   AS "IATA",
        a.name        AS "Aeroporto",
        ci_aero.name  AS "Cidade do Aeroporto",
        ROUND(
            (6371 * 2 * asin(sqrt(
                power(sin(radians((a.latitude_deg  - ci_ref.latitude::float)  / 2)), 2) +
                cos(radians(ci_ref.latitude::float)) * cos(radians(a.latitude_deg)) *
                power(sin(radians((a.longitude_deg - ci_ref.longitude::float) / 2)), 2)
            )))::NUMERIC, 2
        ) AS "Distância (km)",
        at.type AS "Tipo"
    FROM cities ci_ref
    JOIN countries co_ref  ON co_ref.id  = ci_ref.country_id
    JOIN airports a        ON (
        6371 * 2 * asin(sqrt(
            power(sin(radians((a.latitude_deg  - ci_ref.latitude::float)  / 2)), 2) +
            cos(radians(ci_ref.latitude::float)) * cos(radians(a.latitude_deg)) *
            power(sin(radians((a.longitude_deg - ci_ref.longitude::float) / 2)), 2)
        )) <= 100
    )
    JOIN airport_types at  ON at.id      = a.airport_type_id
    JOIN cities ci_aero    ON ci_aero.id = a.city_id
    JOIN countries co_aero ON co_aero.id = ci_aero.country_id
    WHERE ci_ref.name ILIKE %s
      AND co_ref.code  = 'BR'
      AND co_aero.code = 'BR'
      AND at.type IN ('medium_airport', 'large_airport')
    ORDER BY "Distância (km)"
"""

# ── RELATÓRIO 3 (Admin): hierárquico circuitos ────────────────────────────────

SQL_R3_TOTAL = "SELECT COUNT(*) AS total FROM races"

SQL_R3_CIRCUITO = """
    SELECT
        ci.name                     AS "Circuito",
        COUNT(DISTINCT rc.id)       AS "Corridas",
        MIN(agg.v)                  AS "Min Voltas",
        ROUND(AVG(agg.v), 1)        AS "Média Voltas",
        MAX(agg.v)                  AS "Max Voltas"
    FROM circuits ci
    JOIN races rc ON rc.circuit_id = ci.id
    LEFT JOIN (
        SELECT race_id, SUM(laps) AS v FROM results GROUP BY race_id
    ) agg ON agg.race_id = rc.id
    GROUP BY ci.id, ci.name
    ORDER BY COUNT(DISTINCT rc.id) DESC
"""

SQL_R3_CORRIDA = """
    SELECT
        ci.name                     AS "Circuito",
        rc.race_name                AS "Corrida",
        rc.race_date                AS "Data",
        COALESCE(MAX(res.laps), 0)  AS "Voltas",
        COUNT(res.id)               AS "Participantes"
    FROM circuits ci
    JOIN races rc  ON rc.circuit_id = ci.id
    LEFT JOIN results res ON res.race_id = rc.id
    GROUP BY ci.id, ci.name, rc.id, rc.race_name, rc.race_date
    ORDER BY ci.name, rc.race_date
"""

# ── RELATÓRIO 4 (Escuderia): pilotos + vitórias ───────────────────────────────

SQL_R4 = """
    SELECT
        d.given_name || ' ' || d.family_name            AS "Piloto",
        COUNT(*) FILTER (WHERE r.position_order = 1)    AS "Vitórias"
    FROM results r
    JOIN drivers d ON d.id = r.driver_id
    WHERE r.constructor_id = %s
    GROUP BY d.id, d.given_name, d.family_name
    ORDER BY "Vitórias" DESC
"""

# ── RELATÓRIO 5 (Escuderia): resultados por status da escuderia ───────────────

SQL_R5 = """
    SELECT
        st.status AS "Status",
        COUNT(*)  AS "Quantidade"
    FROM results r
    JOIN status st ON st.id = r.status_id
    WHERE r.constructor_id = %s
    GROUP BY st.status
    ORDER BY COUNT(*) DESC
"""

# ── RELATÓRIO 6 (Piloto): pontos por ano ─────────────────────────────────────

SQL_R6 = """
    SELECT
        s.year       AS "Ano",
        rc.race_name AS "Corrida",
        SUM(r.points) AS "Pontos"
    FROM results r
    JOIN races   rc ON rc.id = r.race_id
    JOIN seasons s  ON s.id  = rc.season_id
    WHERE r.driver_id = %s
    GROUP BY s.year, rc.id, rc.race_name
    ORDER BY s.year, rc.race_name
"""

# ── RELATÓRIO 7 (Piloto): resultados por status do piloto ────────────────────

SQL_R7 = """
    SELECT
        st.status AS "Status",
        COUNT(*)  AS "Quantidade"
    FROM results r
    JOIN status st ON st.id = r.status_id
    WHERE r.driver_id = %s
    GROUP BY st.status
    ORDER BY COUNT(*) DESC
"""

# ── AÇÕES ADMIN: cadastro ─────────────────────────────────────────────────────

SQL_INSERT_CONSTRUCTOR = """
    INSERT INTO constructors (id, constructor_ref, name, nationality, country_id, wikipedia_url)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

SQL_INSERT_DRIVER = """
    INSERT INTO drivers (id, driver_ref, given_name, family_name, nationality, date_of_birth)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

# ── AÇÃO ESCUDERIA: busca piloto por sobrenome ────────────────────────────────

SQL_BUSCA_PILOTO = """
    SELECT DISTINCT
        d.given_name || ' ' || d.family_name AS "Nome Completo",
        d.date_of_birth                      AS "Nascimento",
        d.nationality                        AS "Nacionalidade"
    FROM drivers d
    JOIN results r ON r.driver_id = d.id
    WHERE d.family_name ILIKE %s
      AND r.constructor_id = %s
"""

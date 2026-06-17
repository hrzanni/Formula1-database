-- fn_vitorias_escuderia: corridas com position_order = 1

CREATE FUNCTION fn_vitorias_escuderia(p_constructor_id VARCHAR)
RETURNS INTEGER LANGUAGE sql STABLE AS $$
    SELECT COUNT(*)::INTEGER
    FROM results
    WHERE constructor_id = p_constructor_id AND position_order = 1;
$$;

-- fn_pilotos_escuderia: pilotos distintos que correram pela escuderia

CREATE FUNCTION fn_pilotos_escuderia(p_constructor_id VARCHAR)
RETURNS INTEGER LANGUAGE sql STABLE AS $$
    SELECT COUNT(DISTINCT driver_id)::INTEGER
    FROM results
    WHERE constructor_id = p_constructor_id;
$$;

-- fn_anos_escuderia: primeiro e último ano com dados em results

CREATE FUNCTION fn_anos_escuderia(
    p_constructor_id VARCHAR,
    OUT primeiro_ano  INTEGER,
    OUT ultimo_ano    INTEGER
) LANGUAGE sql STABLE AS $$
    SELECT
        MIN(s.year)::INTEGER,
        MAX(s.year)::INTEGER
    FROM results r
    JOIN races   rc ON rc.id = r.race_id
    JOIN seasons s  ON s.id  = rc.season_id
    WHERE r.constructor_id = p_constructor_id;
$$;

-- fn_anos_piloto: primeiro e último ano com dados em results

CREATE FUNCTION fn_anos_piloto(
    p_driver_id  VARCHAR,
    OUT primeiro_ano INTEGER,
    OUT ultimo_ano   INTEGER
) LANGUAGE sql STABLE AS $$
    SELECT
        MIN(s.year)::INTEGER,
        MAX(s.year)::INTEGER
    FROM results r
    JOIN races   rc ON rc.id = r.race_id
    JOIN seasons s  ON s.id  = rc.season_id
    WHERE r.driver_id = p_driver_id;
$$;

-- fn_desempenho_piloto: pontos, vitórias e corridas por ano e circuito

CREATE FUNCTION fn_desempenho_piloto(p_driver_id VARCHAR)
RETURNS TABLE(
    ano      INTEGER,
    circuito VARCHAR,
    pontos   NUMERIC,
    vitorias BIGINT,
    corridas BIGINT
) LANGUAGE sql STABLE AS $$
    SELECT
        s.year,
        rc.race_name,
        SUM(r.points),
        COUNT(*) FILTER (WHERE r.position_order = 1),
        COUNT(*)
    FROM results r
    JOIN races   rc ON rc.id = r.race_id
    JOIN seasons s  ON s.id  = rc.season_id
    WHERE r.driver_id = p_driver_id
    GROUP BY s.year, rc.id, rc.race_name
    ORDER BY s.year, rc.race_name;
$$;

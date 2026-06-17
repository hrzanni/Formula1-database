-- View: resultados agrupados por status

CREATE VIEW vw_resultados_por_status AS
SELECT
    st.status AS nome_status,
    COUNT(*)  AS total
FROM results r
JOIN status st ON st.id = r.status_id
GROUP BY st.status
ORDER BY COUNT(*) DESC;

-- View da temporada mais recente

CREATE VIEW vw_temporada_mais_recente AS
SELECT id, year
FROM seasons
WHERE year = (SELECT MAX(year) FROM seasons);

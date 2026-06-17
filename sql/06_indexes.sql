-- ÍNDICES DE PERFORMANCE

-- R4, R5, fn_vitorias_escuderia, fn_pilotos_escuderia:
CREATE INDEX idx_results_constructor_id
    ON results(constructor_id);

-- R6, R7, fn_desempenho_piloto, fn_anos_piloto:
CREATE INDEX idx_results_driver_id
    ON results(driver_id);

-- R2: JOIN airports → cities por city_id 
CREATE INDEX idx_airports_city_id
    ON airports(city_id);

-- R2: filtro por tipo de aeroporto (medium/large)
CREATE INDEX idx_airports_type_id
    ON airports(airport_type_id);

-- R2: filtro cities.country_id = código Brasil 
CREATE INDEX idx_cities_country_id
    ON cities(country_id);

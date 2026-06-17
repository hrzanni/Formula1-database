-- INSERE EM 'USERS' A PARTIR DAS TABELAS EXISTENTES

-- Admin único
INSERT INTO USERS (login, password, tipo, id_original)
VALUES (
    'admin',
    encode(sha256('admin'::bytea), 'hex'),
    'Admin',
    NULL
)
ON CONFLICT (login) DO NOTHING;

-- Escuderias: login = constructor_ref + '_c', senha = sha256(constructor_ref)
INSERT INTO USERS (login, password, tipo, id_original)
SELECT
    c.constructor_ref || '_c',
    encode(sha256(c.constructor_ref::bytea), 'hex'),
    'Escuderia',
    c.id
FROM constructors c
ON CONFLICT (login) DO NOTHING;

-- Pilotos: login = driver_ref + '_d', senha = sha256(driver_ref)
INSERT INTO USERS (login, password, tipo, id_original)
SELECT
    d.driver_ref || '_d',
    encode(sha256(d.driver_ref::bytea), 'hex'),
    'Piloto',
    d.id
FROM drivers d
ON CONFLICT (login) DO NOTHING;

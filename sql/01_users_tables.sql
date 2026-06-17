-- TABELA USERS
-- Controle de acesso com três perfis: Admin, Escuderia, Piloto
-- Senha armazenada como hash SHA-256 (hex, 64 chars)

CREATE TABLE USERS (
    userid      SERIAL PRIMARY KEY,
    login       VARCHAR(100) NOT NULL UNIQUE,
    password    CHAR(64)     NOT NULL,
    tipo        VARCHAR(10)  NOT NULL CHECK (tipo IN ('Admin','Escuderia','Piloto')),
    id_original VARCHAR(100)
);

-- TABELA USERS_LOG
-- Auditoria de login e logout com timestamp automático

CREATE TABLE USERS_LOG (
    id         SERIAL PRIMARY KEY,
    userid     INTEGER NOT NULL REFERENCES USERS(userid),
    tipo_acao  VARCHAR(10) NOT NULL CHECK (tipo_acao IN ('LOGIN','LOGOUT')),
    data_hora  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_login ON USERS(login);
CREATE INDEX idx_users_log_uid ON USERS_LOG(userid);

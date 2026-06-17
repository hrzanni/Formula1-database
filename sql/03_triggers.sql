-- TRIGGER: Criar usuário ao inserir nova escuderia
-- Lança exceção se login já existir

CREATE FUNCTION fn_criar_usuario_escuderia()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM USERS WHERE login = NEW.constructor_ref || '_c') THEN
        RAISE EXCEPTION 'Login % já existe em USERS.', NEW.constructor_ref || '_c';
    END IF;
    INSERT INTO USERS (login, password, tipo, id_original)
    VALUES (
        NEW.constructor_ref || '_c',
        encode(sha256(NEW.constructor_ref::bytea), 'hex'),
        'Escuderia',
        NEW.id
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS TR_Constructors_User ON constructors;
CREATE TRIGGER TR_Constructors_User
AFTER INSERT ON constructors
FOR EACH ROW EXECUTE FUNCTION fn_criar_usuario_escuderia();


-- TRIGGER: Criar usuário ao inserir novo piloto

CREATE FUNCTION fn_criar_usuario_piloto()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM USERS WHERE login = NEW.driver_ref || '_d') THEN
        RAISE EXCEPTION 'Login % já existe em USERS.', NEW.driver_ref || '_d';
    END IF;
    INSERT INTO USERS (login, password, tipo, id_original)
    VALUES (
        NEW.driver_ref || '_d',
        encode(sha256(NEW.driver_ref::bytea), 'hex'),
        'Piloto',
        NEW.id
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS TR_Drivers_User ON drivers;
CREATE TRIGGER TR_Drivers_User
AFTER INSERT ON drivers
FOR EACH ROW EXECUTE FUNCTION fn_criar_usuario_piloto();

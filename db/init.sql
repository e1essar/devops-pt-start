DO $$
BEGIN
    -- Проверка существования базы данных
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'db_bot') THEN
        -- Создание базы данных, если она не существует
        CREATE DATABASE db_bot;
    END IF;

    -- Проверка существования пользователя repl_user
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'repl_user') THEN
        -- Создание пользователя для репликации
        CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'ubuntu';
    END IF;

    -- Проверка существования репликационного слота
    IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replication_slot') THEN
        -- Создание репликационного слота
        PERFORM pg_create_physical_replication_slot('replication_slot');
    END IF;

    -- Предоставление разрешений пользователю для репликации
    GRANT CONNECT ON DATABASE db_bot TO repl_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO repl_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO repl_user;
    GRANT pg_read_all_data TO repl_user;
    GRANT pg_write_all_data TO repl_user;
    GRANT ALL PRIVILEGES ON DATABASE db_bot TO repl_user;

    -- Предоставление разрешений пользователю postgres
    GRANT ALL PRIVILEGES ON DATABASE db_bot TO postgres;

    -- Проверка существования таблицы email_addresses
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'email_addresses') THEN
        -- Создание таблицы email_addresses
        CREATE TABLE email_addresses (
            id serial PRIMARY KEY,
            email VARCHAR(50)
        );
    END IF;

    -- Проверка существования таблицы phone_numbers
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'phone_numbers') THEN
        -- Создание таблицы phone_numbers
        CREATE TABLE phone_numbers (
            id serial PRIMARY KEY,
            phone_number VARCHAR(255)
        );
    END IF;

END $$;
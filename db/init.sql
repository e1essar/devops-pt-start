DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'db_bot') THEN
        CREATE DATABASE db_bot;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'repl_user') THEN
        CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'replpass';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replication_slot') THEN
        PERFORM pg_create_physical_replication_slot('replication_slot');
    END IF;

    GRANT CONNECT ON DATABASE db_bot TO repl_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO repl_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO repl_user;
    GRANT pg_read_all_data TO repl_user;
    GRANT pg_write_all_data TO repl_user;
    GRANT ALL PRIVILEGES ON DATABASE db_bot TO repl_user;
    GRANT ALL PRIVILEGES ON DATABASE db_bot TO postgres;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'email_addresses') THEN
        CREATE TABLE email_addresses (
            id serial PRIMARY KEY,
            email VARCHAR(50)
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'phone_numbers') THEN
        CREATE TABLE phone_numbers (
            id serial PRIMARY KEY,
            phone_number VARCHAR(255)
        );
    END IF;

END $$;

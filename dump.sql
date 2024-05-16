-- Check if the database exists
SELECT 'CREATE DATABASE db_bot' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_bot');

-- Connect to the default database
\c postgres;

-- Create the "db_bot" database if it doesn't exist
CREATE DATABASE db_bot;

-- Connect to the "db_bot" database
\c db_bot;

-- Create the "email_addresses" table if not exists
CREATE TABLE IF NOT EXISTS email_addresses(
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

-- Create the "phone_numbers" table if not exists
CREATE TABLE IF NOT EXISTS phone_numbers(
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(255) NOT NULL
);

-- Check if the user "repluser" exists, create if not
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'repluser') THEN
        CREATE USER repluser WITH REPLICATION ENCRYPTED PASSWORD 'replpass'; 
    END IF; 
END $$;

-- Change password for user "postgres"
ALTER USER postgres WITH PASSWORD 'postgres';

-- Grant privileges to the user "repluser" for the "db_bot" database
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO repluser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO repluser;
GRANT pg_read_all_data TO repluser;
GRANT pg_write_all_data TO repluser;
GRANT ALL PRIVILEGES ON DATABASE db_bot TO repluser;
GRANT ALL PRIVILEGES ON DATABASE db_bot TO postgres;


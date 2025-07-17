-- Clinical Sample Service Database Initialization Script

-- Create database if it doesn't exist
-- (This is typically handled by the POSTGRES_DB environment variable)

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create initial database schema (tables will be created by Alembic migrations)
-- This file is primarily for any initial setup that needs to happen before migrations

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Clinical Sample Service database initialized successfully';
END $$;
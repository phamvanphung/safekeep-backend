-- Manual migration SQL for vaults table
-- Run this if Alembic migration fails

-- Add name column with default value
ALTER TABLE vaults ADD COLUMN IF NOT EXISTS name VARCHAR NOT NULL DEFAULT 'default_vault';

-- Remove unique constraint on user_id (if exists)
ALTER TABLE vaults DROP CONSTRAINT IF EXISTS vaults_user_id_key;

-- Remove the default after adding (so future inserts require name)
ALTER TABLE vaults ALTER COLUMN name DROP DEFAULT;

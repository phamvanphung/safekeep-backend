#!/bin/bash

echo "🔄 Running database migration to add vault name column..."

# Run the migration
docker compose exec web alembic upgrade head

echo "✅ Migration complete!"
echo ""
echo "📝 If you see errors, you may need to manually run SQL:"
echo "ALTER TABLE vaults ADD COLUMN name VARCHAR NOT NULL DEFAULT 'default_vault';"
echo "ALTER TABLE vaults DROP CONSTRAINT IF EXISTS vaults_user_id_key;"
echo "ALTER TABLE vaults ALTER COLUMN name DROP DEFAULT;"

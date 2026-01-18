# Database Migration Notes

## Important: Vault Model Changes

The Vault model has been updated to support **multiple vaults per user**:

### Changes:
1. **Removed** `unique=True` constraint on `user_id` in the `vaults` table
2. **Added** `name` field (String, required) to identify different vaults

### Migration Required:

You need to create and run an Alembic migration:

```bash
# Create migration
docker compose exec web alembic revision --autogenerate -m "Update vault model for multiple vaults per user"

# Review the migration file in alembic/versions/

# Apply migration
docker compose exec web alembic upgrade head
```

### Manual Migration (if needed):

If you have existing data, you may need to:

1. Add the `name` column with a default value
2. Remove the unique constraint on `user_id`

SQL (run in PostgreSQL):
```sql
-- Add name column
ALTER TABLE vaults ADD COLUMN name VARCHAR NOT NULL DEFAULT 'default_vault';

-- Remove unique constraint (if exists)
ALTER TABLE vaults DROP CONSTRAINT IF EXISTS vaults_user_id_key;
```

### Breaking Changes:

- **Vault API endpoints changed:**
  - Old: `/vault` (single vault per user)
  - New: `/vaults` (multiple vaults per user)
  - Now requires `vault_id` in GET/PUT/DELETE operations

- **Vault creation now requires `name` field**

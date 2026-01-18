"""add vault name column

Revision ID: 001_add_vault_name
Revises: 
Create Date: 2026-01-18 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_vault_name'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add name column to vaults table
    op.add_column('vaults', sa.Column('name', sa.String(), nullable=False, server_default='default_vault'))
    
    # Remove unique constraint on user_id if it exists
    # First check if the constraint exists by trying to drop it
    try:
        op.drop_constraint('vaults_user_id_key', 'vaults', type_='unique')
    except Exception:
        # Constraint doesn't exist, that's fine
        pass
    
    # Remove the server default after adding the column (for future inserts)
    op.alter_column('vaults', 'name', server_default=None)


def downgrade() -> None:
    # Remove name column
    op.drop_column('vaults', 'name')
    
    # Re-add unique constraint on user_id (if needed)
    op.create_unique_constraint('vaults_user_id_key', 'vaults', ['user_id'])

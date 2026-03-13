"""Add RESTRICT constraint to role_permissions foreign key

Revision ID: add_restrict_constraint
Revises: xyz123
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_restrict_constraint'
down_revision = '4c2950a19dcd'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing foreign key constraint
    op.drop_constraint(
        'role_permissions_permission_id_fkey',
        'role_permissions',
        type_='foreignkey'
    )
    
    # Add new foreign key constraint with ON DELETE RESTRICT
    # This prevents deletion of a permission if it's assigned to any role
    op.create_foreign_key(
        'role_permissions_permission_id_fkey',
        'role_permissions',
        'permissions',
        ['permission_id'],
        ['id'],
        ondelete='RESTRICT'
    )


def downgrade():
    # Drop the RESTRICT constraint
    op.drop_constraint(
        'role_permissions_permission_id_fkey',
        'role_permissions',
        type_='foreignkey'
    )
    
    # Restore the original foreign key constraint without RESTRICT
    op.create_foreign_key(
        'role_permissions_permission_id_fkey',
        'role_permissions',
        'permissions',
        ['permission_id'],
        ['id']
    )

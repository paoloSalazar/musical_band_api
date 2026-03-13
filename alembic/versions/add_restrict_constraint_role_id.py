"""Add RESTRICT constraint to role_permissions for role_id

Revision ID: add_restrict_constraint_role_id
Revises: add_restrict_constraint
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_restrict_constraint_role_id'
down_revision = 'add_restrict_constraint'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing foreign key constraint for role_id
    op.drop_constraint(
        'role_permissions_role_id_fkey',
        'role_permissions',
        type_='foreignkey'
    )
    
    # Add new foreign key constraint with ON DELETE RESTRICT
    # This prevents deletion of a role if it has permissions assigned
    op.create_foreign_key(
        'role_permissions_role_id_fkey',
        'role_permissions',
        'user_roles',
        ['role_id'],
        ['id'],
        ondelete='RESTRICT'
    )


def downgrade():
    # Drop the RESTRICT constraint
    op.drop_constraint(
        'role_permissions_role_id_fkey',
        'role_permissions',
        type_='foreignkey'
    )
    
    # Restore the original foreign key constraint without RESTRICT
    op.create_foreign_key(
        'role_permissions_role_id_fkey',
        'role_permissions',
        'user_roles',
        ['role_id'],
        ['id']
    )

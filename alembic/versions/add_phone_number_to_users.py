"""Add phone_number column to users table

Revision ID: add_phone_number_to_users
Revises: add_restrict_constraint_role_id
Create Date: 2026-03-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_phone_number_to_users'
down_revision = 'add_restrict_constraint_role_id'
branch_labels = None
depends_on = None


def upgrade():
    # Add phone_number column to users table
    op.add_column(
        'users',
        sa.Column('phone_number', sa.String(50), nullable=True)
    )


def downgrade():
    # Remove phone_number column from users table
    op.drop_column('users', 'phone_number')

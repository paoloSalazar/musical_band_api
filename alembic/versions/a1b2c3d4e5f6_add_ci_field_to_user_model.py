"""Add CI (DNI) field to User model

Revision ID: a1b2c3d4e5f6
Revises: 6195322f0754
Create Date: 2026-06-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6195322f0754'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ci column to users table"""
    op.add_column('users', sa.Column('ci', sa.String(20), nullable=True))


def downgrade() -> None:
    """Remove ci column from users table"""
    op.drop_column('users', 'ci')
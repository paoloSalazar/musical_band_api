"""Merge CI field and musician event payments migrations

Revision ID: d5bc9ddda396
Revises: a1b2c3d4e5f6, b6e6ebe3f762
Create Date: 2026-06-20 00:19:41.763931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5bc9ddda396'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'b6e6ebe3f762')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

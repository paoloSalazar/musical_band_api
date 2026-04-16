"""add_composite_fk_musician_event_payments

Revision ID: b6e6ebe3f762
Revises: db95bce4c6a5
Create Date: 2026-04-16 06:23:48.114238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6e6ebe3f762'
down_revision: Union[str, None] = 'db95bce4c6a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, add unique constraint to event_musicians to prevent duplicate assignments
    op.create_unique_constraint(
        'uq_event_musician_assignment',
        'event_musicians',
        ['event_id', 'musician_id']
    )

    # Then add composite foreign key constraint to ensure payments reference valid assignments
    op.create_foreign_key(
        'fk_musician_event_assignment',
        'musician_event_payments',
        'event_musicians',
        ['event_id', 'musician_id'],
        ['event_id', 'musician_id'],
        ondelete='RESTRICT'
    )


def downgrade() -> None:
    # Drop the composite foreign key constraint first
    op.drop_constraint('fk_musician_event_assignment', 'musician_event_payments')

    # Then drop the unique constraint
    op.drop_constraint('uq_event_musician_assignment', 'event_musicians')

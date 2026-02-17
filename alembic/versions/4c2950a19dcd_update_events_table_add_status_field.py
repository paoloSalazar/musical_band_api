"""update_events_table add status field

Revision ID: 4c2950a19dcd
Revises: 2ed339ad517f
Create Date: 2026-02-17 08:32:41.776085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c2950a19dcd'
down_revision: Union[str, None] = '2ed339ad517f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type first
    event_status_enum = sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', name='eventstatus')
    event_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Add the column with the enum type
    op.add_column('events', sa.Column('status', event_status_enum, server_default='PENDING', nullable=False))


def downgrade() -> None:
    # Drop the column first
    op.drop_column('events', 'status')
    
    # Drop the enum type
    event_status_enum = sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', name='eventstatus')
    event_status_enum.drop(op.get_bind(), checkfirst=True)

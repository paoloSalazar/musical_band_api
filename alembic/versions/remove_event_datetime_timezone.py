"""Remove timezone from event datetime columns

Revision ID: remove_event_datetime_timezone
Revises: 5e1045d595ae
Create Date: 2026-03-23 11:12:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'remove_event_datetime_timezone'
down_revision = '5e1045d595ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change start_datetime and end_datetime from TIMESTAMP WITH TIME ZONE to TIMESTAMP WITHOUT TIME ZONE
    op.alter_column('events', 'start_datetime',
                   type_=sa.DateTime(timezone=False),
                   existing_type=sa.DateTime(timezone=True),
                   nullable=False)
    op.alter_column('events', 'end_datetime',
                   type_=sa.DateTime(timezone=False),
                   existing_type=sa.DateTime(timezone=True),
                   nullable=False)


def downgrade() -> None:
    # Revert back to TIMESTAMP WITH TIME ZONE
    op.alter_column('events', 'start_datetime',
                   type_=sa.DateTime(timezone=True),
                   existing_type=sa.DateTime(timezone=False),
                   nullable=False)
    op.alter_column('events', 'end_datetime',
                   type_=sa.DateTime(timezone=True),
                   existing_type=sa.DateTime(timezone=False),
                   nullable=False)

"""add_unique_constraint_user_detail_type

Revision ID: uq_user_detail_type
Revises: add_phone_number_to_users, create_user_details_table
Create Date: 2026-03-17 10:56:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'uq_user_detail_type'
down_revision = ('add_phone_number_to_users', 'create_user_details_table')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, check if there are any duplicate (user_id, detail_type) combinations
    # If there are, we need to handle them before adding the constraint
    
    # Delete duplicate records, keeping only the one with the lowest id
    op.execute("""
        DELETE FROM user_details
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM user_details
            GROUP BY user_id, detail_type
        )
    """)
    
    # Add unique constraint on (user_id, detail_type)
    op.create_unique_constraint(
        'uq_user_detail_type',
        'user_details',
        ['user_id', 'detail_type']
    )


def downgrade() -> None:
    op.drop_constraint('uq_user_detail_type', 'user_details', type_='unique')

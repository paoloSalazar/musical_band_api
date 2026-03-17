"""Create user_details table

Revision ID: create_user_details_table
Revises: add_phone_number_to_users
Create Date: 2026-03-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_user_details_table'
down_revision = '4c2950a19dcd'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_details table
    op.create_table(
        'user_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('detail_type', sa.String(50), nullable=False),
        sa.Column('detail_value', sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_details_id', 'user_details', ['id'])
    op.create_index('ix_user_details_user_id', 'user_details', ['user_id'])


def downgrade():
    op.drop_index('ix_user_details_user_id', table_name='user_details')
    op.drop_index('ix_user_details_id', table_name='user_details')
    op.drop_table('user_details')

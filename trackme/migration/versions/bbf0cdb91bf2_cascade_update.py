"""cascade update

Revision ID: bbf0cdb91bf2
Revises: 77b10804413c
Create Date: 2021-04-25 19:43:15.690361

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bbf0cdb91bf2'
down_revision = '77b10804413c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tracking_attributes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_edited_at', sa.DateTime(), nullable=True),
    sa.Column('attribute_id', sa.Integer(), nullable=True),
    sa.Column('tracking_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ),
    sa.ForeignKeyConstraint(['tracking_id'], ['tracking.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('attributes_2_entry')
    op.drop_column('tracking', 'deleted_at')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracking', sa.Column('deleted_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.create_table('attributes_2_entry',
    sa.Column('attribute_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('tracking_entry_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], name='attributes_2_entry_attribute_id_fkey'),
    sa.ForeignKeyConstraint(['tracking_entry_id'], ['tracking.id'], name='attributes_2_entry_tracking_entry_id_fkey')
    )
    op.drop_table('tracking_attributes')
    # ### end Alembic commands ###

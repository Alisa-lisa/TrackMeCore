"""rename tracking attributes column

Revision ID: 066da6651017
Revises: bbf0cdb91bf2
Create Date: 2021-04-30 22:02:21.861661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '066da6651017'
down_revision = 'bbf0cdb91bf2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tracking_attributes', 'last_edited_at')
    op.add_column('tracking_attributes', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tracking_attributes', 'deleted_at')
    op.add_column('tracking_attributes', sa.Column('last_edited_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###

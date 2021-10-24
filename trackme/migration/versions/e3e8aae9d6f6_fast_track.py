"""fast track

Revision ID: e3e8aae9d6f6
Revises: 7c4f5d21d1f2
Create Date: 2021-06-08 21:56:46.580574

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e3e8aae9d6f6"
down_revision = "7c4f5d21d1f2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("tracking", "attribute_id", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("tracking", "attribute_id", existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###

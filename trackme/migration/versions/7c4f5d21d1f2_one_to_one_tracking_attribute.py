"""one to one tracking attribute

Revision ID: 7c4f5d21d1f2
Revises: f6463442b828
Create Date: 2021-06-03 12:53:13.379724

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7c4f5d21d1f2"
down_revision = "f6463442b828"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tracking_attributes")
    op.add_column("tracking", sa.Column("attribute_id", sa.Integer(), nullable=False))
    op.add_column("tracking", sa.Column("stale", sa.Boolean(), nullable=True))
    op.create_foreign_key("tracking_attributes_fk", "tracking", "attributes", ["attribute_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("tracking_attributes_fk", "tracking", type_="foreignkey")
    op.drop_column("tracking", "stale")
    op.drop_column("tracking", "attribute_id")
    op.create_table(
        "tracking_attributes",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column("attribute_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("tracking_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["attribute_id"], ["attributes.id"], name="tracking_attributes_attribute_id_fkey"),
        sa.ForeignKeyConstraint(
            ["tracking_id"], ["tracking.id"], name="tracking_attributes_tracking_id_fkey", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="tracking_attributes_pkey"),
    )
    # ### end Alembic commands ###
"""experiments

Revision ID: 578c234df99c
Revises: c7a39b442939
Create Date: 2022-02-16 17:13:18.947619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "578c234df99c"
down_revision = "c7a39b442939"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "experiments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("experiments")
    # ### end Alembic commands ###

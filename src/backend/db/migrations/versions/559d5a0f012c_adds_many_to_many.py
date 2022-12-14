"""adds many-to-many

Revision ID: 559d5a0f012c
Revises: 2cde15d4576c
Create Date: 2022-09-07 12:12:38.529204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "559d5a0f012c"
down_revision = "2cde15d4576c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "association_item_author",
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["author.id"],
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["item.id"],
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("association_item_author")
    # ### end Alembic commands ###

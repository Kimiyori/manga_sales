"""add unique restraints

Revision ID: 6d61c9c181e8
Revises: 559d5a0f012c
Create Date: 2022-09-08 09:41:10.558686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6d61c9c181e8"
down_revision = "559d5a0f012c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "author", ["name"])
    op.add_column("title", sa.Column("name", sa.String(length=256), nullable=False))
    op.create_unique_constraint(None, "title", ["name"])
    op.drop_column("title", "original_name")
    op.drop_column("title", "english_name")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "title",
        sa.Column(
            "english_name", sa.VARCHAR(length=256), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "title",
        sa.Column(
            "original_name", sa.VARCHAR(length=256), autoincrement=False, nullable=False
        ),
    )
    op.drop_constraint(None, "title", type_="unique")
    op.drop_column("title", "name")
    op.drop_constraint(None, "author", type_="unique")
    # ### end Alembic commands ###
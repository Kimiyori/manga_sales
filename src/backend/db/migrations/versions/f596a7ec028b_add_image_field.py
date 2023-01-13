"""add image field

Revision ID: f596a7ec028b
Revises: b335c97353b6
Create Date: 2022-09-17 17:17:05.533106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f596a7ec028b"
down_revision = "b335c97353b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("item", sa.Column("image", sa.String(), nullable=True))
    op.create_unique_constraint(None, "item", ["image"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "item", type_="unique")
    op.drop_column("item", "image")
    # ### end Alembic commands ###
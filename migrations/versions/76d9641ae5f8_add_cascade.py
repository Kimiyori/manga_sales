"""add cascade

Revision ID: 76d9641ae5f8
Revises: e25b35390327
Create Date: 2022-09-13 11:09:07.679236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76d9641ae5f8'
down_revision = 'e25b35390327'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('title_item_id_fkey', 'title', type_='foreignkey')
    op.create_foreign_key(None, 'title', 'item', ['item_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('week_item_id_fkey', 'week', type_='foreignkey')
    op.create_foreign_key(None, 'week', 'item', ['item_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'week', type_='foreignkey')
    op.create_foreign_key('week_item_id_fkey', 'week', 'item', ['item_id'], ['id'])
    op.drop_constraint(None, 'title', type_='foreignkey')
    op.create_foreign_key('title_item_id_fkey', 'title', 'item', ['item_id'], ['id'])
    # ### end Alembic commands ###

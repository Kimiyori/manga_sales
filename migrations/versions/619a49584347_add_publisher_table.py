"""add publisher table

Revision ID: 619a49584347
Revises: 6d61c9c181e8
Create Date: 2022-09-13 09:25:37.955939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '619a49584347'
down_revision = '6d61c9c181e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('publisher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('association_item_publisher',
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('publisher_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.id'], )
    )
    op.add_column('item', sa.Column('publisher_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'item', 'publisher', ['publisher_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_column('item', 'publisher_id')
    op.drop_table('association_item_publisher')
    op.drop_table('publisher')
    # ### end Alembic commands ###

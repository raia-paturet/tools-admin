"""empty message

Revision ID: 4622412e17e9
Revises: efc8da1e2518
Create Date: 2021-04-07 13:18:32.754566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4622412e17e9'
down_revision = 'efc8da1e2518'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('folder_promo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('promo_id', sa.Integer(), nullable=True),
    sa.Column('folder_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['folder_type_id'], ['folder_type.id'], ),
    sa.ForeignKeyConstraint(['promo_id'], ['promo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('folder_promo')
    # ### end Alembic commands ###
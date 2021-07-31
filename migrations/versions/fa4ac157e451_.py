"""empty message

Revision ID: fa4ac157e451
Revises: 1dd38c8ee6c9
Create Date: 2021-03-14 17:44:40.293521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa4ac157e451'
down_revision = '1dd38c8ee6c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('document_folder',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_type_id', sa.Integer(), nullable=True),
    sa.Column('folder_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['document_type_id'], ['document_type.id'], ),
    sa.ForeignKeyConstraint(['folder_type_id'], ['folder_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('folder_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('document_folder_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['document_folder_id'], ['promo.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('folder_user')
    op.drop_table('document_folder')
    op.drop_table('document_type')
    # ### end Alembic commands ###

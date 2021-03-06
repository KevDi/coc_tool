"""Member Table

Revision ID: cd3daf7a56e3
Revises: 2a7da4009fe5
Create Date: 2020-07-11 14:30:57.631353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd3daf7a56e3'
down_revision = '2a7da4009fe5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('member',
    sa.Column('id', sa.String(length=12), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('th_level', sa.Integer(), nullable=True),
    sa.Column('queen_level', sa.Integer(), nullable=True),
    sa.Column('warden_level', sa.Integer(), nullable=True),
    sa.Column('royal_level', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_member_name'), 'member', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_member_name'), table_name='member')
    op.drop_table('member')
    # ### end Alembic commands ###

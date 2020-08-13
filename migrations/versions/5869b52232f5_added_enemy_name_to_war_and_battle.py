"""Added Enemy Name to War and Battle

Revision ID: 5869b52232f5
Revises: 28e948def274
Create Date: 2020-08-13 12:57:12.718689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5869b52232f5'
down_revision = '28e948def274'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('battle', sa.Column('enemy_name', sa.String(length=64), nullable=False))
    op.add_column('war', sa.Column('enemy_tag', sa.String(length=12), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('war', 'enemy_tag')
    op.drop_column('battle', 'enemy_name')
    # ### end Alembic commands ###

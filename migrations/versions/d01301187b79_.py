"""empty message

Revision ID: d01301187b79
Revises: 3425c53a31f8
Create Date: 2019-03-06 18:00:51.797210

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd01301187b79'
down_revision = '3425c53a31f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('day', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('describe', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('full_name', sa.String(length=1000), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('grad_year', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('hackathons', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('mlh_rules', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('month', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('race', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('school', sa.String(length=1000), nullable=True))
    op.add_column('users', sa.Column('why', sa.String(length=1800), nullable=True))
    op.add_column('users', sa.Column('year', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'year')
    op.drop_column('users', 'why')
    op.drop_column('users', 'school')
    op.drop_column('users', 'race')
    op.drop_column('users', 'month')
    op.drop_column('users', 'mlh_rules')
    op.drop_column('users', 'hackathons')
    op.drop_column('users', 'grad_year')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'describe')
    op.drop_column('users', 'day')
    # ### end Alembic commands ###

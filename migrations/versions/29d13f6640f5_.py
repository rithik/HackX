"""empty message

Revision ID: 29d13f6640f5
Revises: 08d865e0fce9
Create Date: 2019-05-13 23:05:34.847990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29d13f6640f5'
down_revision = '08d865e0fce9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tickets', 'hackerid',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_foreign_key(None, 'tickets', 'hackers', ['hackerid'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tickets', type_='foreignkey')
    op.alter_column('tickets', 'hackerid',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###

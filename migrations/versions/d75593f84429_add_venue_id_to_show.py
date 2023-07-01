"""add venue id to Show

Revision ID: d75593f84429
Revises: adf08dbb953f
Create Date: 2023-07-01 16:37:38.688461

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd75593f84429'
down_revision = 'adf08dbb953f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('venue_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'Venue', ['venue_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('venue_id')

    # ### end Alembic commands ###
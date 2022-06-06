"""Update remonder date's field2

Revision ID: 66ebf6c554d4
Revises: bcd07934a5ec
Create Date: 2022-06-06 09:53:39.225948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66ebf6c554d4'
down_revision = 'bcd07934a5ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vehicle', sa.Column('gen', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vehicle', 'gen')
    # ### end Alembic commands ###

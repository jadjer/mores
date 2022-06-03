"""remove name from location

Revision ID: 67e3b446b7a7
Revises: b054b578fc04
Create Date: 2022-06-02 21:11:48.883450

"""
#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67e3b446b7a7'
down_revision = 'b054b578fc04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('locations', 'description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_constraint('locations_name_key', 'locations', type_='unique')
    op.drop_column('locations', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('locations', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_unique_constraint('locations_name_key', 'locations', ['name'])
    op.alter_column('locations', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###

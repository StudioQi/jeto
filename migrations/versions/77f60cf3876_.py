"""domain controller

Revision ID: 77f60cf3876
Revises: 51b66b3d835a
Create Date: 2014-11-18 23:07:19.925959

Adding the domain controller table
"""

# revision identifiers, used by Alembic.
revision = '77f60cf3876'
# down_revision = '51b66b3d835a'
down_revision = '522a1ad5eb0c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'domain_controller',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('address', sa.String(length=256), nullable=True),
        sa.Column('port', sa.String(length=4), nullable=True),
        sa.Column('accept_self_signed', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('domain_controller')

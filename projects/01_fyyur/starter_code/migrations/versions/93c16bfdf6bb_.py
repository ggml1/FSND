"""empty message

Revision ID: 93c16bfdf6bb
Revises: 424467ac7b55
Create Date: 2020-08-03 00:09:48.415020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93c16bfdf6bb'
down_revision = '424467ac7b55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###

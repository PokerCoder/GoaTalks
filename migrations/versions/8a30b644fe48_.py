"""empty message

Revision ID: 8a30b644fe48
Revises: 7cf49f786452
Create Date: 2022-07-02 04:16:44.291957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a30b644fe48'
down_revision = '7cf49f786452'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contact_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=True),
    sa.Column('email', sa.String(length=140), nullable=True),
    sa.Column('subject', sa.String(length=140), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contact_history')
    # ### end Alembic commands ###

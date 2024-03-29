"""empty message

Revision ID: 914b490c2a9b
Revises: 57bf896ef087
Create Date: 2024-02-25 14:58:57.193674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '914b490c2a9b'
down_revision = '57bf896ef087'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('difficulty', sa.String(length=10), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer_logs', schema=None) as batch_op:
        batch_op.drop_column('difficulty')

    # ### end Alembic commands ###

"""empty message

Revision ID: 93e859b4c848
Revises: 65c12efcfb95
Create Date: 2024-02-01 10:57:17.586880

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '93e859b4c848'
down_revision = '65c12efcfb95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('email_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('info', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('email_logs', schema=None) as batch_op:
        batch_op.drop_column('info')

    # ### end Alembic commands ###

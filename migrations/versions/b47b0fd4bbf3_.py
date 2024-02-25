"""empty message

Revision ID: b47b0fd4bbf3
Revises: eb38c0fe0b52
Create Date: 2024-02-25 12:55:31.868958

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b47b0fd4bbf3'
down_revision = 'eb38c0fe0b52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('answer_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('real_answer', sa.String(length=100), nullable=True),
    sa.Column('user_answer', sa.String(length=100), nullable=True),
    sa.Column('correct', sa.Boolean(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('answer_logs')
    # ### end Alembic commands ###

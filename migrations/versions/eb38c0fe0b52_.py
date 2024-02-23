"""empty message

Revision ID: eb38c0fe0b52
Revises: d5bfc1ea1301
Create Date: 2024-02-23 18:34:26.914355

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'eb38c0fe0b52'
down_revision = 'd5bfc1ea1301'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('high_score', 'high_scores')


def downgrade():
    op.rename_table('high_scores', 'high_score')

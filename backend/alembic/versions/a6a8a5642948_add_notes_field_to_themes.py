"""add notes field to themes

Revision ID: a6a8a5642948
Revises: f6c0aa4b96a8
Create Date: 2026-08-21 23:10:12.944437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6a8a5642948'
down_revision: Union[str, Sequence[str], None] = 'f6c0aa4b96a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # A server_default is required so existing rows get a value for the new NOT NULL column
    # (SQLite's ADD COLUMN rejects NOT NULL without one on a non-empty table) — dropped again
    # right after, same two-step approach as the owner_id migration.
    with op.batch_alter_table('themes') as batch_op:
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=False, server_default=''))

    with op.batch_alter_table('themes') as batch_op:
        batch_op.alter_column('notes', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('themes') as batch_op:
        batch_op.drop_column('notes')

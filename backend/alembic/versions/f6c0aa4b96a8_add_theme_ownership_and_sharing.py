"""add theme ownership and sharing

Revision ID: f6c0aa4b96a8
Revises: 05e60a89b541
Create Date: 2026-08-16 19:13:33.561664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6c0aa4b96a8'
down_revision: Union[str, Sequence[str], None] = '05e60a89b541'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('theme_shares',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('theme_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('theme_id', 'user_id', name='uq_theme_shares_theme_user')
    )
    op.create_index(op.f('ix_theme_shares_id'), 'theme_shares', ['id'], unique=False)

    # SQLite has no ALTER TABLE support for adding a constraint, so the column + FK are
    # added together via batch mode (copy-and-move strategy) instead of the two separate
    # op.add_column()/op.create_foreign_key() calls autogenerate produced.
    with op.batch_alter_table('themes') as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.Integer(), nullable=False, server_default='1'))
        batch_op.create_foreign_key('fk_themes_owner_id_users', 'users', ['owner_id'], ['id'])

    with op.batch_alter_table('themes') as batch_op:
        batch_op.alter_column('owner_id', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('themes') as batch_op:
        batch_op.drop_constraint('fk_themes_owner_id_users', type_='foreignkey')
        batch_op.drop_column('owner_id')

    op.drop_index(op.f('ix_theme_shares_id'), table_name='theme_shares')
    op.drop_table('theme_shares')

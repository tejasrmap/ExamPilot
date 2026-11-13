"""add structured_options_json to questions table

Revision ID: 0001_struct_opts
Revises: 
Create Date: 2026-11-14 00:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_struct_opts'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'questions' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('questions')]
        if 'structured_options_json' not in columns:
            op.add_column('questions', sa.Column('structured_options_json', sa.Text(), nullable=True))

def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'questions' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('questions')]
        if 'structured_options_json' in columns:
            op.drop_column('questions', 'structured_options_json')


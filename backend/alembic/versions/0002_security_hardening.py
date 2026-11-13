"""security hardening: token_version, password_reset_tokens, practice session questions, durable storage

Revision ID: 0002_security_hardening
Revises: 0001_struct_opts
Create Date: 2026-11-14 01:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0002_security_hardening'
down_revision: Union[str, None] = '0001_struct_opts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. Add token_version to profiles table
    if 'profiles' in tables:
        columns = [c['name'] for c in inspector.get_columns('profiles')]
        if 'token_version' not in columns:
            op.add_column('profiles', sa.Column('token_version', sa.Integer(), nullable=False, server_default='1'))

    # 2. Create password_reset_tokens table
    if 'password_reset_tokens' not in tables:
        op.create_table(
            'password_reset_tokens',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('user_id', sa.String(length=36), sa.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False),
            sa.Column('token_hash', sa.String(length=64), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('used_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
        op.create_index('ix_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'])
        op.create_index('ix_password_reset_tokens_expires_at', 'password_reset_tokens', ['expires_at'])

    # 3. Add question_ids_json to practice_sessions table
    if 'practice_sessions' in tables:
        columns = [c['name'] for c in inspector.get_columns('practice_sessions')]
        if 'question_ids_json' not in columns:
            op.add_column('practice_sessions', sa.Column('question_ids_json', sa.Text(), nullable=True))

    # 4. Add storage_provider and storage_key to documents table
    if 'documents' in tables:
        columns = [c['name'] for c in inspector.get_columns('documents')]
        if 'storage_provider' not in columns:
            op.add_column('documents', sa.Column('storage_provider', sa.String(length=30), nullable=False, server_default='local'))
        if 'storage_key' not in columns:
            op.add_column('documents', sa.Column('storage_key', sa.String(length=500), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'documents' in tables:
        columns = [c['name'] for c in inspector.get_columns('documents')]
        if 'storage_key' in columns:
            op.drop_column('documents', 'storage_key')
        if 'storage_provider' in columns:
            op.drop_column('documents', 'storage_provider')

    if 'practice_sessions' in tables:
        columns = [c['name'] for c in inspector.get_columns('practice_sessions')]
        if 'question_ids_json' in columns:
            op.drop_column('practice_sessions', 'question_ids_json')

    if 'password_reset_tokens' in tables:
        op.drop_table('password_reset_tokens')

    if 'profiles' in tables:
        columns = [c['name'] for c in inspector.get_columns('profiles')]
        if 'token_version' in columns:
            op.drop_column('profiles', 'token_version')


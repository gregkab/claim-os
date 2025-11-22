"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create claims table
    op.create_table(
        'claims',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('reference_number', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_claims_id'), 'claims', ['id'], unique=False)
    op.create_index(op.f('ix_claims_owner_user_id'), 'claims', ['owner_user_id'], unique=False)
    op.create_index(op.f('ix_claims_reference_number'), 'claims', ['reference_number'], unique=False)

    # Create files table
    op.create_table(
        'files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('claim_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['claim_id'], ['claims.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_id'), 'files', ['id'], unique=False)
    op.create_index(op.f('ix_files_claim_id'), 'files', ['claim_id'], unique=False)

    # Create artifacts table
    op.create_table(
        'artifacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('claim_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('current_version_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['claim_id'], ['claims.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artifacts_id'), 'artifacts', ['id'], unique=False)
    op.create_index(op.f('ix_artifacts_claim_id'), 'artifacts', ['claim_id'], unique=False)
    op.create_index(op.f('ix_artifacts_type'), 'artifacts', ['type'], unique=False)

    # Create artifact_versions table
    op.create_table(
        'artifact_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artifact_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('version_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['artifact_id'], ['artifacts.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artifact_versions_id'), 'artifact_versions', ['id'], unique=False)
    op.create_index(op.f('ix_artifact_versions_artifact_id'), 'artifact_versions', ['artifact_id'], unique=False)

    # Add foreign key for artifacts.current_version_id after artifact_versions table exists
    op.create_foreign_key(
        'fk_artifacts_current_version_id',
        'artifacts', 'artifact_versions',
        ['current_version_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_artifacts_current_version_id', 'artifacts', type_='foreignkey')
    op.drop_index(op.f('ix_artifact_versions_artifact_id'), table_name='artifact_versions')
    op.drop_index(op.f('ix_artifact_versions_id'), table_name='artifact_versions')
    op.drop_table('artifact_versions')
    op.drop_index(op.f('ix_artifacts_type'), table_name='artifacts')
    op.drop_index(op.f('ix_artifacts_claim_id'), table_name='artifacts')
    op.drop_index(op.f('ix_artifacts_id'), table_name='artifacts')
    op.drop_table('artifacts')
    op.drop_index(op.f('ix_files_claim_id'), table_name='files')
    op.drop_index(op.f('ix_files_id'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_claims_reference_number'), table_name='claims')
    op.drop_index(op.f('ix_claims_owner_user_id'), table_name='claims')
    op.drop_index(op.f('ix_claims_id'), table_name='claims')
    op.drop_table('claims')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')


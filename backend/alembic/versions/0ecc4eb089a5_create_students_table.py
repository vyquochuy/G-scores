"""create_students_table

Revision ID: 0ecc4eb089a5
Revises:
Create Date: 2026-10-17 12:38:03.705787

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0ecc4eb089a5'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sbd', sa.String(length=8), nullable=False),
        sa.Column('toan', sa.Float(), nullable=True),
        sa.Column('ngu_van', sa.Float(), nullable=True),
        sa.Column('ngoai_ngu', sa.Float(), nullable=True),
        sa.Column('vat_li', sa.Float(), nullable=True),
        sa.Column('hoa_hoc', sa.Float(), nullable=True),
        sa.Column('sinh_hoc', sa.Float(), nullable=True),
        sa.Column('lich_su', sa.Float(), nullable=True),
        sa.Column('dia_li', sa.Float(), nullable=True),
        sa.Column('gdcd', sa.Float(), nullable=True),
        sa.Column('ma_ngoai_ngu', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_students_sbd'), 'students', ['sbd'], unique=True)
    op.create_index(op.f('ix_students_toan'), 'students', ['toan'], unique=False)
    op.create_index(op.f('ix_students_vat_li'), 'students', ['vat_li'], unique=False)
    op.create_index(op.f('ix_students_hoa_hoc'), 'students', ['hoa_hoc'], unique=False)
    op.create_index('idx_group_a_subjects', 'students', ['toan', 'vat_li', 'hoa_hoc'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_group_a_subjects', table_name='students')
    op.drop_index(op.f('ix_students_hoa_hoc'), table_name='students')
    op.drop_index(op.f('ix_students_vat_li'), table_name='students')
    op.drop_index(op.f('ix_students_toan'), table_name='students')
    op.drop_index(op.f('ix_students_sbd'), table_name='students')
    op.drop_table('students')

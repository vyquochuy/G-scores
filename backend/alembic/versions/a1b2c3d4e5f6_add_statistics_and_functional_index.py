"""add_statistics_and_functional_index

Revision ID: a1b2c3d4e5f6
Revises: 0ecc4eb089a5
Create Date: 2026-10-19 13:35:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "0ecc4eb089a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Tao bang system_metrics
    op.create_table(
        "system_metrics",
        sa.Column("metric_key", sa.String(length=50), nullable=False),
        sa.Column("metric_value", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("metric_key"),
    )

    # 2. Tao bang score_statistics
    op.create_table(
        "score_statistics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject_code", sa.String(length=20), nullable=False),
        sa.Column("ge_8", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ge_6_lt_8", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ge_4_lt_6", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lt_4", sa.Integer(), server_default="0", nullable=False),
        sa.Column("valid_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_score_statistics_subject_code"),
        "score_statistics",
        ["subject_code"],
        unique=True,
    )

    # 3. Tao Partial Functional Index cho Top 10 Khoi A
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_students_group_a_sum
        ON students (
            (toan + vat_li + hoa_hoc) DESC,
            sbd ASC
        )
        WHERE toan IS NOT NULL
          AND vat_li IS NOT NULL
          AND hoa_hoc IS NOT NULL;
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_students_group_a_sum;")
    op.drop_index(op.f("ix_score_statistics_subject_code"), table_name="score_statistics")
    op.drop_table("score_statistics")
    op.drop_table("system_metrics")

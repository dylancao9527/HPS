"""split admin users table

Revision ID: f4a9d2c6b8e1
Revises: 8b9c2d1e4f73
Create Date: 2026-05-07 18:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f4a9d2c6b8e1"
down_revision = "8b9c2d1e4f73"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_admin_users")),
    )
    with op.batch_alter_table("admin_users", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_admin_users_email"), ["email"], unique=True)
        batch_op.create_index(
            batch_op.f("ix_admin_users_username"),
            ["username"],
            unique=True,
        )

    op.execute(
        """
        INSERT INTO admin_users (username, email, password_hash, created_at)
        SELECT username, email, password_hash, created_at
        FROM users
        WHERE role = 'admin'
        """
    )

    _delete_admin_user_dependencies()
    op.execute("DELETE FROM users WHERE role = 'admin'")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("role")


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("role", sa.String(length=10), nullable=False, server_default="user")
        )

    op.execute(
        """
        INSERT INTO users (username, email, password_hash, role, created_at)
        SELECT username, email, password_hash, 'admin', created_at
        FROM admin_users
        """
    )

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("role", server_default=None)

    with op.batch_alter_table("admin_users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_admin_users_username"))
        batch_op.drop_index(batch_op.f("ix_admin_users_email"))
    op.drop_table("admin_users")


def _delete_admin_user_dependencies():
    admin_user_ids = "SELECT id FROM users WHERE role = 'admin'"
    admin_prediction_ids = (
        "SELECT id FROM prediction_records "
        f"WHERE user_id IN ({admin_user_ids})"
    )
    admin_prophet_prediction_ids = (
        "SELECT id FROM prophet_predictions "
        f"WHERE user_id IN ({admin_user_ids})"
    )

    op.execute(
        "DELETE FROM prediction_recommendations "
        f"WHERE prediction_record_id IN ({admin_prediction_ids})"
    )
    op.execute(
        "DELETE FROM prediction_input_snapshots "
        f"WHERE prediction_record_id IN ({admin_prediction_ids})"
    )
    op.execute(
        "DELETE FROM prediction_fusion_meta "
        f"WHERE prediction_record_id IN ({admin_prediction_ids})"
    )
    op.execute(
        "DELETE FROM prediction_confidence_reasons "
        f"WHERE prediction_record_id IN ({admin_prediction_ids})"
    )
    op.execute(f"DELETE FROM prediction_records WHERE user_id IN ({admin_user_ids})")
    op.execute(
        "DELETE FROM prediction_training_meta "
        f"WHERE prophet_prediction_id IN ({admin_prophet_prediction_ids})"
    )
    op.execute(
        "DELETE FROM prophet_forecast_points "
        f"WHERE prophet_prediction_id IN ({admin_prophet_prediction_ids})"
    )
    op.execute(f"DELETE FROM prophet_predictions WHERE user_id IN ({admin_user_ids})")
    op.execute(f"DELETE FROM user_prophet_models WHERE user_id IN ({admin_user_ids})")
    op.execute(f"DELETE FROM bp_records WHERE user_id IN ({admin_user_ids})")
    op.execute(f"DELETE FROM user_profiles WHERE user_id IN ({admin_user_ids})")

"""slim prophet model persistence

Revision ID: 3d7a1b9c0e2f
Revises: 2a7f1c9d8e44
Create Date: 2026-05-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "3d7a1b9c0e2f"
down_revision = "2a7f1c9d8e44"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    table = "user_prophet_models"

    with op.batch_alter_table(table, schema=None) as batch_op:
        _drop_index_if_exists(
            batch_op,
            bind,
            table,
            "ix_user_prophet_models_active_slot_trained",
        )
        _drop_check_if_exists(
            batch_op,
            bind,
            table,
            "ck_user_prophet_models_forecast_days_7",
        )
        if _has_column(bind, table, "forecast_days"):
            batch_op.drop_column("forecast_days")
        batch_op.create_index(
            "ix_user_prophet_models_active_slot_trained",
            ["user_id", "is_active", "trained_at", "id"],
            unique=False,
        )


def downgrade():
    bind = op.get_bind()
    table = "user_prophet_models"

    with op.batch_alter_table(table, schema=None) as batch_op:
        _drop_index_if_exists(
            batch_op,
            bind,
            table,
            "ix_user_prophet_models_active_slot_trained",
        )
        if not _has_column(bind, table, "forecast_days"):
            batch_op.add_column(
                sa.Column(
                    "forecast_days",
                    sa.Integer(),
                    nullable=False,
                    server_default="7",
                )
            )
        _create_check_if_missing(
            batch_op,
            bind,
            table,
            "ck_user_prophet_models_forecast_days_7",
            "forecast_days = 7",
        )
        batch_op.create_index(
            "ix_user_prophet_models_active_slot_trained",
            ["user_id", "forecast_days", "is_active", "trained_at", "id"],
            unique=False,
        )


def _has_column(bind, table_name, column_name):
    return column_name in {
        column["name"] for column in inspect(bind).get_columns(table_name)
    }


def _drop_index_if_exists(batch_op, bind, table_name, index_name):
    names = {index["name"] for index in inspect(bind).get_indexes(table_name)}
    if index_name in names:
        batch_op.drop_index(index_name)


def _drop_check_if_exists(batch_op, bind, table_name, constraint_name):
    names = {
        constraint["name"]
        for constraint in inspect(bind).get_check_constraints(table_name)
    }
    if constraint_name in names:
        batch_op.drop_constraint(constraint_name, type_="check")


def _create_check_if_missing(batch_op, bind, table_name, constraint_name, condition):
    names = {
        constraint["name"]
        for constraint in inspect(bind).get_check_constraints(table_name)
    }
    if constraint_name not in names:
        batch_op.create_check_constraint(constraint_name, condition)

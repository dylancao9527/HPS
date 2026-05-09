"""enforce 7 day forecast period

Revision ID: 8b9c2d1e4f73
Revises: 6fd55bac034c
Create Date: 2026-05-07 13:05:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '8b9c2d1e4f73'
down_revision = '6fd55bac034c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE prophet_predictions SET forecast_days = 7 WHERE forecast_days <> 7")
    op.execute("UPDATE user_prophet_models SET forecast_days = 7 WHERE forecast_days <> 7")

    with op.batch_alter_table('prophet_predictions', schema=None) as batch_op:
        batch_op.create_check_constraint(
            op.f('ck_prophet_predictions_forecast_days_7'),
            'forecast_days = 7',
        )

    with op.batch_alter_table('user_prophet_models', schema=None) as batch_op:
        batch_op.create_check_constraint(
            op.f('ck_user_prophet_models_forecast_days_7'),
            'forecast_days = 7',
        )


def downgrade():
    with op.batch_alter_table('user_prophet_models', schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f('ck_user_prophet_models_forecast_days_7'),
            type_='check',
        )

    with op.batch_alter_table('prophet_predictions', schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f('ck_prophet_predictions_forecast_days_7'),
            type_='check',
        )

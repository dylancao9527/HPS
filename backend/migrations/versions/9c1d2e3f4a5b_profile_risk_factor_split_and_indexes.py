"""split user risk factor profile and add query indexes

Revision ID: 9c1d2e3f4a5b
Revises: f4a9d2c6b8e1
Create Date: 2026-05-07 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9c1d2e3f4a5b"
down_revision = "f4a9d2c6b8e1"
branch_labels = None
depends_on = None


RISK_FACTOR_COLUMNS = (
    "age",
    "male",
    "height",
    "weight",
    "current_smoker",
    "cigs_per_day",
    "bp_meds",
    "diabetes",
    "tot_chol",
    "glucose",
)


def upgrade():
    _allow_optional_prediction_input_fields()

    op.create_table(
        "user_risk_factor_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("age", sa.Float(), nullable=True),
        sa.Column("male", sa.Integer(), nullable=True),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("current_smoker", sa.Integer(), nullable=True),
        sa.Column("cigs_per_day", sa.Float(), nullable=True),
        sa.Column("bp_meds", sa.Integer(), nullable=True),
        sa.Column("diabetes", sa.Integer(), nullable=True),
        sa.Column("tot_chol", sa.Float(), nullable=True),
        sa.Column("glucose", sa.Float(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_risk_factor_profiles_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_risk_factor_profiles")),
    )
    with op.batch_alter_table("user_risk_factor_profiles", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_user_risk_factor_profiles_user_id"),
            ["user_id"],
            unique=True,
        )

    op.execute(
        """
        INSERT INTO user_risk_factor_profiles (
            user_id,
            age,
            male,
            height,
            weight,
            current_smoker,
            cigs_per_day,
            bp_meds,
            diabetes,
            tot_chol,
            glucose,
            updated_at
        )
        SELECT
            user_id,
            age,
            male,
            height,
            weight,
            current_smoker,
            cigs_per_day,
            bp_meds,
            diabetes,
            tot_chol,
            glucose,
            updated_at
        FROM user_profiles
        """
    )

    with op.batch_alter_table("user_profiles", schema=None) as batch_op:
        for column_name in RISK_FACTOR_COLUMNS:
            batch_op.drop_column(column_name)

    _create_query_indexes()


def downgrade():
    _drop_query_indexes()

    with op.batch_alter_table("user_profiles", schema=None) as batch_op:
        batch_op.add_column(sa.Column("age", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("male", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("height", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("weight", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("current_smoker", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("cigs_per_day", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("bp_meds", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("diabetes", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("tot_chol", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("glucose", sa.Float(), nullable=True))

    op.execute(
        """
        INSERT INTO user_profiles (user_id, updated_at)
        SELECT r.user_id, r.updated_at
        FROM user_risk_factor_profiles r
        LEFT JOIN user_profiles p ON p.user_id = r.user_id
        WHERE p.user_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE user_profiles
        SET
            age = (
                SELECT r.age
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            male = (
                SELECT r.male
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            height = (
                SELECT r.height
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            weight = (
                SELECT r.weight
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            current_smoker = (
                SELECT r.current_smoker
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            cigs_per_day = (
                SELECT r.cigs_per_day
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            bp_meds = (
                SELECT r.bp_meds
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            diabetes = (
                SELECT r.diabetes
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            tot_chol = (
                SELECT r.tot_chol
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            ),
            glucose = (
                SELECT r.glucose
                FROM user_risk_factor_profiles r
                WHERE r.user_id = user_profiles.user_id
            )
        WHERE user_id IN (
            SELECT user_id
            FROM user_risk_factor_profiles
        )
        """
    )

    with op.batch_alter_table("user_risk_factor_profiles", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_risk_factor_profiles_user_id"))
    op.drop_table("user_risk_factor_profiles")

    _restore_required_prediction_input_fields()


def _allow_optional_prediction_input_fields():
    with op.batch_alter_table("prediction_input_snapshots", schema=None) as batch_op:
        batch_op.alter_column(
            "current_smoker",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
        )
        batch_op.alter_column(
            "bp_meds",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
        )
        batch_op.alter_column(
            "diabetes",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
        )

    with op.batch_alter_table("prediction_fusion_meta", schema=None) as batch_op:
        batch_op.alter_column(
            "bp_meds_input",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
        )


def _restore_required_prediction_input_fields():
    op.execute(
        """
        UPDATE prediction_input_snapshots
        SET
            current_smoker = COALESCE(current_smoker, 0),
            bp_meds = COALESCE(bp_meds, 0),
            diabetes = COALESCE(diabetes, 0)
        """
    )
    op.execute(
        """
        UPDATE prediction_fusion_meta
        SET bp_meds_input = COALESCE(bp_meds_input, 0)
        """
    )

    with op.batch_alter_table("prediction_fusion_meta", schema=None) as batch_op:
        batch_op.alter_column(
            "bp_meds_input",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
        )

    with op.batch_alter_table("prediction_input_snapshots", schema=None) as batch_op:
        batch_op.alter_column(
            "diabetes",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
        )
        batch_op.alter_column(
            "bp_meds",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
        )
        batch_op.alter_column(
            "current_smoker",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
        )


def _create_query_indexes():
    with op.batch_alter_table("bp_records", schema=None) as batch_op:
        batch_op.create_index(
            "ix_bp_records_user_recorded_at",
            ["user_id", "recorded_at"],
            unique=False,
        )

    with op.batch_alter_table("prediction_records", schema=None) as batch_op:
        batch_op.create_index(
            "ix_prediction_records_user_created_at",
            ["user_id", "created_at"],
            unique=False,
        )
        batch_op.create_index(
            "ix_prediction_records_risk_created_at",
            ["risk_level", "created_at"],
            unique=False,
        )

    with op.batch_alter_table("prophet_predictions", schema=None) as batch_op:
        batch_op.create_index(
            "ix_prophet_predictions_user_created_at",
            ["user_id", "created_at"],
            unique=False,
        )

    with op.batch_alter_table("user_prophet_models", schema=None) as batch_op:
        batch_op.create_index(
            "ix_user_prophet_models_active_slot_trained",
            ["user_id", "forecast_days", "is_active", "trained_at", "id"],
            unique=False,
        )

    with op.batch_alter_table("prediction_training_meta", schema=None) as batch_op:
        batch_op.create_index(
            "ix_prediction_training_meta_confidence_prophet",
            ["confidence_level", "prophet_prediction_id"],
            unique=False,
        )


def _drop_query_indexes():
    with op.batch_alter_table("prediction_training_meta", schema=None) as batch_op:
        batch_op.drop_index("ix_prediction_training_meta_confidence_prophet")

    with op.batch_alter_table("user_prophet_models", schema=None) as batch_op:
        batch_op.drop_index("ix_user_prophet_models_active_slot_trained")

    with op.batch_alter_table("prophet_predictions", schema=None) as batch_op:
        batch_op.drop_index("ix_prophet_predictions_user_created_at")

    with op.batch_alter_table("prediction_records", schema=None) as batch_op:
        batch_op.drop_index("ix_prediction_records_risk_created_at")
        batch_op.drop_index("ix_prediction_records_user_created_at")

    with op.batch_alter_table("bp_records", schema=None) as batch_op:
        batch_op.drop_index("ix_bp_records_user_recorded_at")

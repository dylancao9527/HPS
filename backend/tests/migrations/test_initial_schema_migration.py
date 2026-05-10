import ast
from pathlib import Path


MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "migrations"
    / "versions"
    / "75f5fe8065f4_initial_schema.py"
)


def test_initial_schema_downgrade_drops_tables_without_manual_index_drops():
    module = ast.parse(MIGRATION_PATH.read_text(encoding="utf-8"))
    downgrade = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "downgrade"
    )
    calls = [
        node
        for node in ast.walk(downgrade)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    ]
    call_names = [node.func.attr for node in calls]

    assert "drop_index" not in call_names

    drop_tables = [
        node.args[0].value
        for node in calls
        if node.func.attr == "drop_table"
        and node.args
        and isinstance(node.args[0], ast.Constant)
    ]
    assert drop_tables[:5] == [
        "user_risk_factor_profiles",
        "user_prophet_models",
        "user_profiles",
        "prediction_records",
        "bp_records",
    ]

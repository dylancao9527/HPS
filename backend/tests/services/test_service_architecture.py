import ast
from pathlib import Path


def test_service_modules_do_not_depend_on_route_modules():
    services_dir = Path(__file__).resolve().parents[2] / "services"
    offenders = []

    for path in sorted(services_dir.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "routes" or module.startswith("routes."):
                    offenders.append(f"{path.name}:{node.lineno} imports {module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "routes" or alias.name.startswith("routes."):
                        offenders.append(
                            f"{path.name}:{node.lineno} imports {alias.name}"
                        )

    assert not offenders, (
        "Service modules should depend on contracts or adapters, not route modules:\n"
        + "\n".join(offenders)
    )


def test_auth_account_service_is_split_into_auth_subdomain_services():
    path = Path(__file__).resolve().parents[2] / "services" / "auth_service.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    class_names = {
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    }

    assert {
        "RegistrationService",
        "LoginService",
        "AccountMaintenanceService",
        "PasswordResetService",
    }.issubset(class_names)

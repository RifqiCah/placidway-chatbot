import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def assert_layer_does_not_import(layer: str, forbidden: tuple[str, ...]) -> None:
    violations: list[str] = []
    for path in (APP_ROOT / layer).rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith(forbidden):
                violations.append(f"{path.relative_to(APP_ROOT)} imports {module}")
    assert not violations, "Dependency rule violations:\n" + "\n".join(violations)


def test_domain_has_no_outward_dependencies() -> None:
    assert_layer_does_not_import(
        "domain",
        (
            "backend.app.api",
            "backend.app.application",
            "backend.app.core",
            "backend.app.infrastructure",
            "fastapi",
            "httpx",
            "pydantic",
        ),
    )


def test_application_does_not_depend_on_delivery_or_infrastructure() -> None:
    assert_layer_does_not_import(
        "application",
        ("backend.app.api", "backend.app.core", "backend.app.infrastructure", "fastapi", "httpx", "pydantic"),
    )


import ast
from pathlib import Path


SCAN_ENGINE_PATH = Path("app/scan_engine")
FORBIDDEN_IMPORT_PREFIXES = (
    "fastapi",
    "celery",
    "redis",
    "app.services",
)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_scan_engine_has_no_forbidden_framework_or_prototype_imports() -> None:
    for path in SCAN_ENGINE_PATH.glob("*.py"):
        for imported_module in imported_modules(path):
            assert not imported_module.startswith(
                FORBIDDEN_IMPORT_PREFIXES
            ), f"{path} imports forbidden module {imported_module}"


def test_runner_is_the_only_scan_engine_module_that_commits() -> None:
    for path in SCAN_ENGINE_PATH.glob("*.py"):
        if path.name == "runner.py":
            continue
        source = path.read_text(encoding="utf-8")
        assert ".commit(" not in source, (
            f"{path} must not own transaction boundaries"
        )

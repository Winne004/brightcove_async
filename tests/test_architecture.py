"""AST-based tests enforcing import boundaries between architectural layers."""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).parent.parent / "src" / "brightcove_async"


def _package_of(path: Path) -> str:
    """Dotted package name for the directory containing path, relative to src/."""
    return ".".join(path.relative_to(SRC.parent).parent.parts)


def get_internal_imports(path: Path) -> list[str]:
    """Return all brightcove_async.* imports in path, resolving relative imports to absolute."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[str] = []
    package = _package_of(path)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module and node.module.startswith("brightcove_async"):
                    imports.append(node.module)
                    for alias in node.names:
                        if alias.name != "*":
                            imports.append(f"{node.module}.{alias.name}")
            else:
                # Resolve relative import to absolute module path.
                # Level 1 = current package; each extra level goes one package up.
                parts = package.split(".") if package else []
                if node.level > 1:
                    trim = node.level - 1
                    parts = parts[:-trim] if trim < len(parts) else []
                anchor = ".".join(parts)
                if node.module:
                    # `from .module import names` — record the resolved module
                    resolved = f"{anchor}.{node.module}" if anchor else node.module
                    if resolved.startswith("brightcove_async"):
                        imports.append(resolved)
                else:
                    # `from . import name1, name2` — record each resolved name
                    for alias in node.names:
                        resolved = f"{anchor}.{alias.name}" if anchor else alias.name
                        if resolved.startswith("brightcove_async"):
                            imports.append(resolved)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("brightcove_async"):
                    imports.append(alias.name)
    return imports


def _forbidden(imports: list[str], *prefixes: str) -> list[str]:
    return [
        imp
        for imp in imports
        if any(imp == p or imp.startswith(p + ".") for p in prefixes)
    ]


def _schema_files() -> list[Path]:
    return sorted((SRC / "schemas").rglob("*.py"))


def _domain_service_files() -> list[Path]:
    """All service files except base.py (includes __init__.py)."""
    return sorted(p for p in (SRC / "services").glob("*.py") if p.name != "base.py")


def _domain_service_modules() -> list[str]:
    """Absolute module paths for domain services, excluding base.py and __init__.py."""
    return [
        f"brightcove_async.services.{p.stem}"
        for p in (SRC / "services").glob("*.py")
        if p.name not in ("base.py", "__init__.py")
    ]


# Guards: catch broken installs or wrong working directory before tests silently vanish
def test_schema_files_discoverable() -> None:
    assert _schema_files(), (
        f"No .py files found under {SRC / 'schemas'} — check that SRC is correct"
    )


def test_domain_service_files_discoverable() -> None:
    assert _domain_service_files(), (
        f"No service files found under {SRC / 'services'} — check that SRC is correct"
    )


# Rule 1: Foundation modules have no internal imports
@pytest.mark.parametrize(
    "rel_path",
    [
        "settings.py",
        "protocols.py",
        "exceptions.py",
        "oauth/oauth.py",
    ],
)
def test_foundation_isolation(rel_path: str) -> None:
    imports = get_internal_imports(SRC / rel_path)
    assert not imports, (
        f"{rel_path} must not import from brightcove_async; found: {imports}"
    )


# Rule 2: Schemas do not import from services, client, registry, oauth, or exceptions
@pytest.mark.parametrize("path", _schema_files(), ids=lambda p: str(p.relative_to(SRC)))
def test_schema_isolation(path: Path) -> None:
    found = _forbidden(
        get_internal_imports(path),
        "brightcove_async.services",
        "brightcove_async.client",
        "brightcove_async.registry",
        "brightcove_async.oauth",
        "brightcove_async.exceptions",
    )
    assert not found, (
        f"{path.relative_to(SRC)} must not import from services/client/registry/oauth/exceptions; "
        f"found: {found}"
    )


# Rule 3: Base service does not import from domain siblings, client, registry, settings, schemas, or oauth
def test_base_service_isolation() -> None:
    found = _forbidden(
        get_internal_imports(SRC / "services" / "base.py"),
        *_domain_service_modules(),
        "brightcove_async.client",
        "brightcove_async.registry",
        "brightcove_async.settings",
        "brightcove_async.schemas",
        "brightcove_async.oauth",
    )
    assert not found, f"services/base.py must not import {found}"


# Rule 4: Domain services do not import from client, registry, settings, or oauth
@pytest.mark.parametrize(
    "path", _domain_service_files(), ids=lambda p: f"services/{p.name}"
)
def test_domain_service_isolation(path: Path) -> None:
    found = _forbidden(
        get_internal_imports(path),
        "brightcove_async.client",
        "brightcove_async.registry",
        "brightcove_async.settings",
        "brightcove_async.oauth",
    )
    assert not found, (
        f"services/{path.name} must not import from client/registry/settings/oauth; found: {found}"
    )


# Rule 5: Registry does not import from client or initialise
def test_registry_isolation() -> None:
    found = _forbidden(
        get_internal_imports(SRC / "registry.py"),
        "brightcove_async.client",
        "brightcove_async.initialise",
    )
    assert not found, (
        f"registry.py must not import from client/initialise; found: {found}"
    )


# Rule 6: Client does not import from initialise, settings, or oauth
def test_client_isolation() -> None:
    found = _forbidden(
        get_internal_imports(SRC / "client.py"),
        "brightcove_async.initialise",
        "brightcove_async.settings",
        "brightcove_async.oauth",
    )
    assert not found, (
        f"client.py must not import from initialise/settings/oauth; found: {found}"
    )

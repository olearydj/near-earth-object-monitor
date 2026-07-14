from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version


PACKAGE_NAME = "near-earth-object-monitor"
API_KEY_ENV_VAR = "NASA_API_KEY"
RECOMMENDED_DATA_DIRS = ("data/raw/", "data/processed/")
CHECK_COMMANDS = (
    "uv run python -m pytest",
    "uv run pytest --cov=neo_monitor --cov-report=term-missing",
    "uv run ruff format --check .",
    "uv run ruff check .",
    "uv run mypy src",
)


@dataclass(frozen=True)
class ProjectMetadata:
    """Small project state summary for setup and handoff checks."""

    package_name: str
    version: str
    api_key_env_var: str
    api_key_configured: bool
    data_dirs: tuple[str, ...]
    check_commands: tuple[str, ...]


def build_project_metadata(api_key: str | None) -> ProjectMetadata:
    """Build project metadata without calling external services."""

    return ProjectMetadata(
        package_name=PACKAGE_NAME,
        version=package_version(),
        api_key_env_var=API_KEY_ENV_VAR,
        api_key_configured=bool(api_key and api_key.strip()),
        data_dirs=RECOMMENDED_DATA_DIRS,
        check_commands=CHECK_COMMANDS,
    )


def format_project_metadata(metadata: ProjectMetadata) -> str:
    """Format project metadata as plain text."""

    api_key_status = "configured" if metadata.api_key_configured else "missing"
    lines = [
        "Near-Earth Object Monitor Project Info",
        f"Package: {metadata.package_name}",
        f"Version: {metadata.version}",
        f"{metadata.api_key_env_var}: {api_key_status}",
        "Recommended data folders:",
    ]
    lines.extend(f"- {data_dir}" for data_dir in metadata.data_dirs)
    lines.append("Development checks:")
    lines.extend(f"- {command}" for command in metadata.check_commands)
    return "\n".join(lines)


def package_version() -> str:
    """Return the installed package version, or unknown outside an install."""

    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"

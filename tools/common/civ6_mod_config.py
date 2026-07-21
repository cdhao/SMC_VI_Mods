"""Shared TOML manifest support for Civilization VI mod build tooling."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


class ConfigError(ValueError):
    """Raised when a mod build manifest is incomplete or inconsistent."""


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class ModBuildConfig:
    """Repository-relative configuration shared by build, cook, and checks."""

    manifest_path: Path
    repo_root: Path
    slug: str
    release_version: int
    asset_revision: int
    asset_root: Path
    runtime_root: Path
    project_root: Path
    package_templates: Mapping[str, str]

    def render(self, value: str) -> str:
        try:
            return value.format(
                slug=self.slug,
                release_version=self.release_version,
                asset_version=self.asset_revision,
            )
        except KeyError as error:
            raise ConfigError(
                f"Unknown placeholder {error.args[0]!r} in {self.manifest_path}"
            ) from error

    def package(self, key: str) -> str:
        try:
            return self.render(self.package_templates[key])
        except KeyError as error:
            raise ConfigError(f"Missing package {key!r} in {self.manifest_path}") from error

    @property
    def package_names(self) -> tuple[str, ...]:
        return tuple(self.package(key) for key in self.package_templates)


def _require_table(document: Mapping[str, object], key: str, path: Path) -> Mapping[str, object]:
    value = document.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Expected [{key}] table in {path}")
    return value


def _require_string(table: Mapping[str, object], key: str, path: Path) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value:
        raise ConfigError(f"Expected non-empty string {key!r} in {path}")
    return value


def _require_positive_int(table: Mapping[str, object], key: str, path: Path) -> int:
    value = table.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigError(f"Expected positive integer {key!r} in {path}")
    return value


def load_mod_config(path: Path, *, repo_root: Path | None = None) -> ModBuildConfig:
    """Load a mod manifest and validate its paths and package names."""

    path = path.resolve()
    try:
        with path.open("rb") as manifest_file:
            document = tomllib.load(manifest_file)
    except FileNotFoundError as error:
        raise ConfigError(f"Missing mod build manifest: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"Invalid TOML in {path}: {error}") from error

    mod = _require_table(document, "mod", path)
    paths = _require_table(document, "paths", path)
    assets = _require_table(document, "assets", path)
    packages = _require_table(document, "packages", path)

    slug = _require_string(mod, "slug", path)
    if not _IDENTIFIER_PATTERN.fullmatch(slug):
        raise ConfigError(f"Mod slug must be an ASCII identifier in {path}: {slug!r}")

    if not packages:
        raise ConfigError(f"Expected at least one package in {path}")
    package_templates: dict[str, str] = {}
    for key, value in packages.items():
        if not isinstance(key, str) or not _IDENTIFIER_PATTERN.fullmatch(key):
            raise ConfigError(f"Invalid package key {key!r} in {path}")
        if not isinstance(value, str) or not value:
            raise ConfigError(f"Expected non-empty package name for {key!r} in {path}")
        package_templates[key] = value

    resolved_repo_root = (repo_root or path.parents[2]).resolve()
    config = ModBuildConfig(
        manifest_path=path,
        repo_root=resolved_repo_root,
        slug=slug,
        release_version=_require_positive_int(mod, "release_version", path),
        asset_revision=_require_positive_int(assets, "revision", path),
        asset_root=resolved_repo_root / _require_string(paths, "asset_root", path),
        runtime_root=resolved_repo_root / _require_string(paths, "runtime_root", path),
        project_root=resolved_repo_root / _require_string(paths, "project_root", path),
        package_templates=MappingProxyType(package_templates),
    )

    rendered_packages = config.package_names
    if len(rendered_packages) != len(set(rendered_packages)):
        raise ConfigError(f"Manifest has duplicate package names after rendering: {path}")
    for package_name in rendered_packages:
        if not _IDENTIFIER_PATTERN.fullmatch(package_name):
            raise ConfigError(
                f"Package name must be an ASCII identifier in {path}: {package_name!r}"
            )
    return config

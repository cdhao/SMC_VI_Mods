"""Reusable static validation primitives for Civilization VI mod repositories."""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class ValidationError(RuntimeError):
    """Raised when one or more repository contracts are not satisfied."""


@dataclass(frozen=True)
class TextContract:
    path: Path
    required: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
    required_patterns: tuple[str, ...] = ()
    forbidden_patterns: tuple[str, ...] = ()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_file(path: Path) -> None:
    if not path.is_file():
        raise ValidationError(f"Missing required file: {path}")


def require_contains(path: Path, value: str) -> None:
    if value not in read_text(path):
        raise ValidationError(f"Expected {value!r} in {path}")


def require_not_contains(path: Path, value: str) -> None:
    if value in read_text(path):
        raise ValidationError(f"Did not expect {value!r} in {path}")


def require_matches(path: Path, pattern: str) -> None:
    if re.search(pattern, read_text(path), flags=re.MULTILINE | re.DOTALL) is None:
        raise ValidationError(f"Expected pattern {pattern!r} in {path}")


def require_not_matches(path: Path, pattern: str) -> None:
    if re.search(pattern, read_text(path), flags=re.MULTILINE | re.DOTALL) is not None:
        raise ValidationError(f"Did not expect pattern {pattern!r} in {path}")


def require_binary_contains(path: Path, value: str) -> None:
    require_file(path)
    if value.encode("ascii") not in path.read_bytes():
        raise ValidationError(f"Expected binary entry {value!r} in {path}")


def require_binary_not_contains(path: Path, value: str) -> None:
    require_file(path)
    if value.encode("ascii") in path.read_bytes():
        raise ValidationError(f"Did not expect binary entry {value!r} in {path}")


def require_dds_rgba(path: Path, width: int, height: int) -> None:
    require_file(path)
    payload = path.read_bytes()
    if len(payload) < 128 or payload[:4] != b"DDS ":
        raise ValidationError(f"Not a DDS texture: {path}")

    actual_height, actual_width = struct.unpack_from("<II", payload, 12)
    bits_per_pixel = struct.unpack_from("<I", payload, 88)[0]
    fourcc = payload[84:88]
    masks = struct.unpack_from("<IIII", payload, 92)
    legacy_rgba = fourcc == b"\x00\x00\x00\x00" and masks == (
        0x000000FF,
        0x0000FF00,
        0x00FF0000,
        0xFF000000,
    )
    dx10_rgba = (
        fourcc == b"DX10"
        and len(payload) >= 148
        and struct.unpack_from("<I", payload, 128)[0] == 28
    )
    if (actual_width, actual_height, bits_per_pixel) != (width, height, 32):
        raise ValidationError(
            f"Unexpected DDS dimensions for {path}: "
            f"expected {width}x{height}x32, got "
            f"{actual_width}x{actual_height}x{bits_per_pixel}"
        )
    if not (legacy_rgba or dx10_rgba):
        raise ValidationError(f"DDS is not RGBA-compatible with its TEX file: {path}")


def runtime_mod_paths(
    mod_root: Path,
    *,
    project_file_names: set[str] | frozenset[str] = frozenset(),
) -> list[Path]:
    """Return build-only files and directories incorrectly present in a runtime mod."""

    forbidden_roots = ("Images", "XLPs", "Logs")
    forbidden_suffixes = {".tex", ".xlp", ".civ6suo"}
    found: list[Path] = []
    for path in mod_root.rglob("*"):
        relative = path.relative_to(mod_root)
        if relative.parts[0] in forbidden_roots:
            found.append(relative)
        elif path.name in project_file_names or path.suffix.lower() in forbidden_suffixes:
            found.append(relative)
    return sorted(set(found))


def apply_text_contracts(contracts: Iterable[TextContract]) -> None:
    for contract in contracts:
        require_file(contract.path)
        for value in contract.required:
            require_contains(contract.path, value)
        for value in contract.forbidden:
            require_not_contains(contract.path, value)
        for pattern in contract.required_patterns:
            require_matches(contract.path, pattern)
        for pattern in contract.forbidden_patterns:
            require_not_matches(contract.path, pattern)

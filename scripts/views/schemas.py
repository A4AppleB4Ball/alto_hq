"""Item schemas from org/schemas: their file pattern and allowed statuses."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

ITEM_BASE = "item/v1"

# README rule 1: an item id is <TYPE>-<YYYYMMDD>-<HHMM>-<slug>; slugs are kebab-case.
ID_TAIL = r"\d{8}-\d{4}-[a-z0-9][a-z0-9-]*"


@dataclass(frozen=True)
class ItemSchema:
    name: str
    file_pattern: str
    statuses: tuple[str, ...]


def load_item_schemas(root: Path) -> list[ItemSchema]:
    """Every schema that extends item/v1, sorted by name."""
    schemas = []
    for path in sorted((root / "org" / "schemas").glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        if data.get("extends") != ITEM_BASE:
            continue
        if "file" not in data:
            raise ValueError(f"{path}: item schema has no 'file' pattern")
        status = data.get("required", {}).get("status")
        if not isinstance(status, dict) or "values" not in status:
            raise ValueError(f"{path}: item schema has no status values")
        schemas.append(ItemSchema(data["schema"], data["file"], tuple(status["values"])))
    if not schemas:
        raise ValueError(f"{root}: no item schemas found under org/schemas")
    return schemas


def pattern_to_glob(pattern: str) -> str:
    """'engineering/tasks/<year>/T-…/task.md' -> 'engineering/tasks/*/T-*/task.md'."""
    parts = []
    for segment in pattern.split("/"):
        if segment.startswith("<") and segment.endswith(">"):
            parts.append("*")
        else:
            parts.append(segment.replace("…", "*"))
    return "/".join(parts)


def pattern_to_regex(pattern: str) -> re.Pattern:
    """The exact path shape of an item file: '<…>' is one path segment and
    'X-…' is an item id with prefix X (README rule 1). Files beside an item
    that only share its id as a prefix (e.g. 'E-….inventory.md') do not match."""
    parts = []
    for segment in pattern.split("/"):
        if segment.startswith("<") and segment.endswith(">"):
            parts.append(r"[^/]+")
        elif "…" in segment:
            head, tail = segment.split("…")
            parts.append(re.escape(head) + ID_TAIL + re.escape(tail))
        else:
            parts.append(re.escape(segment))
    return re.compile("/".join(parts))

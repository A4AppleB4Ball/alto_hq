"""Item schemas from org/schemas: their file pattern, sidecars and statuses."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

ITEM_BASE = "item/v1"

# README rule 1: an item id is <TYPE>-<YYYYMMDD>-<HHMM>-<slug>; slugs are kebab-case.
ID_TAIL = r"\d{8}-\d{4}-[a-z0-9][a-z0-9-]*"
# version/v1: a version id is v<n> or v<n>.<m> (hotfix); its folder segment is written 'v<n>'.
VERSION_SEGMENT = "v<n>"
VERSION_ID = r"v\d+(?:\.\d+)?"
# A '<year>' segment is a four-digit year.
YEAR_SEGMENT = "<year>"
YEAR = r"\d{4}"


@dataclass(frozen=True)
class ItemSchema:
    name: str
    file_pattern: str
    statuses: tuple[str, ...]
    sidecar_patterns: tuple[str, ...]


def read_sidecars(path: Path, value) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return tuple(value)
    raise ValueError(f"{path}: 'sidecar' must be a pattern or a list of patterns")


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
        schemas.append(ItemSchema(
            data["schema"], data["file"], tuple(status["values"]),
            read_sidecars(path, data.get("sidecar")),
        ))
    if not schemas:
        raise ValueError(f"{root}: no item schemas found under org/schemas")
    return schemas


# A '<name>' placeholder in a pattern segment ('<year>', 'v<n>', '<topic>').
PLACEHOLDER = re.compile(r"<[a-z-]+>")
# What a '<topic>' or other placeholder may be inside an id-bearing segment: kebab-case, no dots.
PLACEHOLDER_IN_ID = r"[a-z0-9][a-z0-9-]*"


def is_id_segment(segment: str) -> bool:
    """The segment that carries the item id: 'X-…' (README rule 1) or 'v<n>' (version/v1)."""
    return "…" in segment or segment == VERSION_SEGMENT


def id_segment_index(pattern: str) -> int:
    """Index of the pattern segment that carries the item id."""
    for index, segment in enumerate(pattern.split("/")):
        if is_id_segment(segment):
            return index
    raise ValueError(f"{pattern}: no id-bearing segment ('X-…' or '{VERSION_SEGMENT}')")


def scan_root(pattern: str) -> str:
    """The literal folder every file of the pattern lives under
    ('engineering/tasks/<year>/T-…/task.md' -> 'engineering/tasks')."""
    literal = []
    for segment in pattern.split("/"):
        if is_id_segment(segment) or PLACEHOLDER.search(segment):
            break
        literal.append(segment)
    if not literal:
        raise ValueError(f"{pattern}: no literal folder before its first placeholder")
    return "/".join(literal)


def segment_to_regex(segment: str) -> str:
    """One pattern segment as a regex. 'X-…' is an item id with prefix X
    (README rule 1); 'v<n>' is a version id; '<year>' is four digits; a
    placeholder beside an id is kebab-case; any other placeholder is one
    path segment."""
    if segment == VERSION_SEGMENT:
        return VERSION_ID
    if segment == YEAR_SEGMENT:
        return YEAR
    if "…" in segment:
        head, tail = segment.split("…")
        tail_parts = PLACEHOLDER.split(tail)
        tail_regex = PLACEHOLDER_IN_ID.join(re.escape(part) for part in tail_parts)
        return re.escape(head) + ID_TAIL + tail_regex
    parts = PLACEHOLDER.split(segment)
    return r"[^/]+".join(re.escape(part) for part in parts)


def pattern_to_regex(pattern: str) -> re.Pattern:
    """The exact path shape of an item file. Files beside an item that only
    share its id as a prefix (e.g. 'E-….inventory.md') do not match."""
    return re.compile("/".join(segment_to_regex(s) for s in pattern.split("/")))

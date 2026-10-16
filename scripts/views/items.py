"""Read and validate the frontmatter of every item file."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from scripts.views.schemas import ItemSchema, id_segment_index, pattern_to_regex, scan_root, segment_to_regex

OWNER_STATUSES = ("awaiting_owner", "needs_owner")


@dataclass(frozen=True)
class Item:
    path: Path
    schema: str
    id: str
    title: str
    status: str
    waiting_on: str | None


class ItemError(ValueError):
    pass


def read_frontmatter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ItemError(f"{path}: no frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ItemError(f"{path}: frontmatter is not closed")
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as error:
        raise ItemError(f"{path}: frontmatter is not valid YAML: {error}") from error
    if not isinstance(data, dict):
        raise ItemError(f"{path}: frontmatter is not a mapping")
    return data


def parse_item(path: Path, schema: ItemSchema) -> Item:
    data = read_frontmatter(path)
    if data.get("schema") != schema.name:
        raise ItemError(f"{path}: schema is {data.get('schema')!r}, expected {schema.name!r}")
    for field in ("id", "title", "status"):
        if field not in data:
            raise ItemError(f"{path}: frontmatter is missing '{field}'")
    status = data["status"]
    if status not in schema.statuses:
        raise ItemError(f"{path}: status {status!r} is not one of {list(schema.statuses)}")
    waiting_on = data.get("waiting_on")
    if status in OWNER_STATUSES and not waiting_on:
        raise ItemError(f"{path}: status {status!r} requires 'waiting_on'")
    return Item(path, schema.name, str(data["id"]), str(data["title"]), status, waiting_on)


def is_sidecar(rel: str, schema: ItemSchema, item_files: set[str]) -> bool:
    """A sidecar matches one of the schema's declared sidecar patterns exactly
    and sits beside an item whose id it starts with ('E-<id>.<topic>.md')."""
    if not any(pattern_to_regex(p).fullmatch(rel) for p in schema.sidecar_patterns):
        return False
    folder, name = rel.rsplit("/", 1)
    return any(
        item.rsplit("/", 1)[0] == folder and name.startswith(item.rsplit("/", 1)[1].removesuffix(".md") + ".")
        for item in item_files
    )


def check_prefix(path: Path, parts: list[str], segments: list[str], schema: ItemSchema) -> None:
    """Every folder between the scan root and the id segment matches its pattern segment."""
    for depth, part in enumerate(parts):
        if not re.fullmatch(segment_to_regex(segments[depth]), part):
            raise ItemError(f"{path}: {part!r} does not match '{segments[depth]}' of {schema.name} ({schema.file_pattern})")


def scan_item_files(root: Path, schema: ItemSchema) -> list[Path]:
    """Every item file of a schema. Every file and folder under the schema's
    scan root must be an item, a declared sidecar beside an existing item, or
    inside an item's own folder; anything else raises naming the path."""
    segments = schema.file_pattern.split("/")
    index = id_segment_index(schema.file_pattern)
    base = scan_root(schema.file_pattern)
    offset = len(base.split("/"))
    shape = pattern_to_regex(schema.file_pattern)
    is_file_item = index == len(segments) - 1
    paths = sorted((root / base).rglob("*"))
    item_files: set[str] = set()
    sidecar_candidates = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        parts = rel.split("/")
        depth = len(parts) - 1
        if depth < index:
            check_prefix(path, parts[offset:], segments[offset:], schema)
            if not path.is_dir():
                raise ItemError(f"{path}: a file where {schema.name} expects a folder ({schema.file_pattern})")
            continue
        check_prefix(path, parts[offset:index], segments[offset:index], schema)
        if is_file_item:
            if depth > index or path.is_dir():
                raise ItemError(f"{path}: not a valid {schema.name} item file ({schema.file_pattern})")
            if shape.fullmatch(rel):
                item_files.add(rel)
            else:
                sidecar_candidates.append(path)
            continue
        folder = root / "/".join(parts[: index + 1])
        if not folder.is_dir() or not re.fullmatch(segment_to_regex(segments[index]), parts[index]):
            raise ItemError(f"{folder}: not a valid {schema.name} item folder ({segments[index]})")
        if depth == index:
            item_file = folder / "/".join(segments[index + 1:])
            if not item_file.is_file():
                raise ItemError(f"{folder}: item folder has no {'/'.join(segments[index + 1:])}")
            item_files.add(item_file.relative_to(root).as_posix())
    for path in sidecar_candidates:
        rel = path.relative_to(root).as_posix()
        if not is_sidecar(rel, schema, item_files):
            raise ItemError(f"{path}: not a valid {schema.name} item file (README rule 1 id) nor a declared sidecar")
    return [root / rel for rel in sorted(item_files)]


def collect_items(root: Path, schemas: list[ItemSchema]) -> list[Item]:
    """Every item file of every item schema, sorted by status then id."""
    items = []
    for schema in schemas:
        for path in scan_item_files(root, schema):
            items.append(parse_item(path, schema))
    return sorted(items, key=lambda item: (item.status, item.id))

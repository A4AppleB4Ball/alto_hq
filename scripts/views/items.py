"""Read and validate the frontmatter of every item file."""

from dataclasses import dataclass
from pathlib import Path

import yaml

from scripts.views.schemas import ItemSchema, pattern_to_glob, pattern_to_regex

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


def id_segment_index(pattern: str) -> int | None:
    """Index of the pattern segment that carries the item id ('X-…'), if any."""
    for index, segment in enumerate(pattern.split("/")):
        if "…" in segment:
            return index
    return None


def is_sidecar(rel: str, schema: ItemSchema, item_files: set[str]) -> bool:
    """A sidecar matches the schema's declared sidecar pattern exactly and
    sits beside an item whose id it starts with (e.g. 'E-<id>.<topic>.md')."""
    if schema.sidecar_pattern is None:
        return False
    if not pattern_to_regex(schema.sidecar_pattern).fullmatch(rel):
        return False
    folder, name = rel.rsplit("/", 1)
    return any(
        item.rsplit("/", 1)[0] == folder and name.startswith(item.rsplit("/", 1)[1].removesuffix(".md") + ".")
        for item in item_files
    )


def scan_item_files(root: Path, schema: ItemSchema) -> list[Path]:
    """Every item file of a schema. Anything that matches the loose shape of
    the id-bearing segment ('T-*', 'E-*.md') but is not a valid item (or a
    declared sidecar) raises naming the path; nothing is skipped silently."""
    segments = schema.file_pattern.split("/")
    shape = pattern_to_regex(schema.file_pattern)
    index = id_segment_index(schema.file_pattern)
    if index is None:
        candidates = sorted(root.glob(pattern_to_glob(schema.file_pattern)))
    else:
        loose = pattern_to_glob("/".join(segments[: index + 1]))
        candidates = sorted(root.glob(loose))
    if index is not None and index < len(segments) - 1:
        rest = "/".join(segments[index + 1:])
        folder_shape = pattern_to_regex("/".join(segments[: index + 1]))
        files = []
        for folder in candidates:
            rel = folder.relative_to(root).as_posix()
            if not folder.is_dir() or not folder_shape.fullmatch(rel):
                raise ItemError(f"{folder}: not a valid {schema.name} item folder (README rule 1 id)")
            item_file = folder / rest
            if not item_file.is_file():
                raise ItemError(f"{folder}: item folder has no {rest}")
            files.append(item_file)
        return files
    rels = {path.relative_to(root).as_posix() for path in candidates}
    item_files = {rel for rel in rels if shape.fullmatch(rel)}
    for path in candidates:
        rel = path.relative_to(root).as_posix()
        if rel in item_files or is_sidecar(rel, schema, item_files):
            continue
        raise ItemError(f"{path}: not a valid {schema.name} item file (README rule 1 id) nor a declared sidecar")
    return [root / rel for rel in sorted(item_files)]


def collect_items(root: Path, schemas: list[ItemSchema]) -> list[Item]:
    """Every item file of every item schema, sorted by status then id."""
    items = []
    for schema in schemas:
        for path in scan_item_files(root, schema):
            items.append(parse_item(path, schema))
    return sorted(items, key=lambda item: (item.status, item.id))

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


def collect_items(root: Path, schemas: list[ItemSchema]) -> list[Item]:
    """Every item file of every item schema, sorted by status then id."""
    items = []
    for schema in schemas:
        shape = pattern_to_regex(schema.file_pattern)
        for path in sorted(root.glob(pattern_to_glob(schema.file_pattern))):
            if not shape.fullmatch(path.relative_to(root).as_posix()):
                continue
            items.append(parse_item(path, schema))
    return sorted(items, key=lambda item: (item.status, item.id))

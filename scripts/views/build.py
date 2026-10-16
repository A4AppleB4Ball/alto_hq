"""Rebuild the generated views of alto_hq (README rules 3-4).

Run from the alto_hq root: python -m scripts.views.build
"""

from pathlib import Path

from scripts.views.items import collect_items
from scripts.views.render import render_approvals, render_by_status
from scripts.views.schemas import load_item_schemas

BY_STATUS = Path("_generated/by_status.md")
APPROVALS = Path("engineering/_generated/approvals.md")


def build(root: Path) -> list[Path]:
    """Validate every item, then write both views. Raises on any bad item."""
    items = collect_items(root, load_item_schemas(root))
    outputs = {
        root / BY_STATUS: render_by_status(items, root / BY_STATUS),
        root / APPROVALS: render_approvals(items, root / APPROVALS),
    }
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return list(outputs)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    for path in build(root):
        print(path.relative_to(root))


if __name__ == "__main__":
    main()

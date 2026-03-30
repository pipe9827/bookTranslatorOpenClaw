"""Terminology memory utilities for glossary loading and candidate extraction."""

from pathlib import Path
import re

MEMORY_DIR = Path(__file__).parent.parent / "memory"
TERMINOLOGY_PATH = MEMORY_DIR / "terminology.md"
CANDIDATES_PATH = MEMORY_DIR / "terminology_candidates.md"

_TABLE_ROW_RE = re.compile(
    r"^\|\s*(?P<source>[^|]+?)\s*\|\s*(?P<target>[^|]+?)\s*\|\s*(?P<notes>[^|]*?)\s*\|?$"
)


def _normalise(text: str) -> str:
    """Normalise text for duplicate comparison."""
    return " ".join(text.strip().split()).lower()


def _parse_markdown_table(path: Path) -> dict[str, str]:
    """Parse a glossary Markdown table into a source->target mapping."""
    if not path.exists():
        return {}

    glossary: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _TABLE_ROW_RE.match(line.strip())
        if not match:
            continue

        source = match.group("source").strip()
        target = match.group("target").strip()

        if _normalise(source) in {"spanish", "---", ""}:
            continue
        if _normalise(target) in {"english", "---", ""}:
            continue

        glossary[source] = target

    return glossary


def load_terminology() -> dict[str, str]:
    """Load the official glossary."""
    return _parse_markdown_table(TERMINOLOGY_PATH)


def load_terminology_candidates() -> dict[str, str]:
    """Load candidate glossary entries."""
    return _parse_markdown_table(CANDIDATES_PATH)


def append_terminology_candidates(candidates_markdown: str) -> None:
    """Append extracted candidate rows to terminology_candidates.md."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not CANDIDATES_PATH.exists():
        CANDIDATES_PATH.write_text(
            "# Terminology Candidates\n\n"
            "| Spanish | English | Notes |\n"
            "|---------|---------|-------|\n",
            encoding="utf-8",
        )

    existing = load_terminology_candidates()
    official = load_terminology()

    existing_keys = {_normalise(key) for key in existing}
    official_keys = {_normalise(key) for key in official}

    rows_to_add: list[str] = []

    for line in candidates_markdown.splitlines():
        match = _TABLE_ROW_RE.match(line.strip())
        if not match:
            continue

        source = " ".join(match.group("source").strip().split())
        target = " ".join(match.group("target").strip().split())
        notes = " ".join(match.group("notes").strip().split())

        if _normalise(source) in {"spanish", "---", ""}:
            continue
        if _normalise(target) in {"english", "---", ""}:
            continue

        normalised_source = _normalise(source)
        if normalised_source in official_keys or normalised_source in existing_keys:
            continue

        rows_to_add.append(f"| {source} | {target} | {notes or 'Candidate'} |")
        existing_keys.add(normalised_source)

    if not rows_to_add:
        return

    current = CANDIDATES_PATH.read_text(encoding="utf-8").rstrip() + "\n"
    current += "\n".join(rows_to_add) + "\n"
    CANDIDATES_PATH.write_text(current, encoding="utf-8")
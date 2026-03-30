"""Utilities for managing a translation terminology glossary."""

import re
from pathlib import Path

TERMINOLOGY_PATH = Path(__file__).resolve().parents[1] / "memory" / "terminology.md"

# Regex to capture rows in a Markdown table: | Spanish | English |
_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
# Matches a separator row such as |---|---| or |---------|---------|
_SEPARATOR_RE = re.compile(r"^[\s|:-]+$")


def load_terminology() -> dict[str, str]:
    """Load the glossary from the terminology memory file.

    Returns:
        A dictionary mapping Spanish terms to their English equivalents.
        Returns an empty dict if the file does not exist or has no entries.
    """
    if not TERMINOLOGY_PATH.exists():
        return {}

    content = TERMINOLOGY_PATH.read_text(encoding="utf-8")
    glossary: dict[str, str] = {}
    rows = list(_ROW_RE.finditer(content))
    for idx, match in enumerate(rows):
        spanish = match.group(1).strip()
        english = match.group(2).strip()
        # Skip the header row (first row) and any separator rows
        if idx == 0 or _SEPARATOR_RE.match(spanish) or _SEPARATOR_RE.match(english):
            continue
        if spanish and english:
            glossary[spanish] = english
    return glossary


def update_terminology(source_text: str, translated_text: str) -> None:
    """Scan *source_text* and *translated_text* for new bold/italic terms.

    Reliable Spanish → English pairing requires LLM involvement because
    positional or alphabetical heuristics produce incorrect mappings.  This
    function therefore collects *candidate* Spanish terms (emphasised phrases
    that are not yet in the glossary) and logs them so that a human reviewer
    or a future LLM-assisted step can add the correct translations.

    To add LLM-based automatic pairing, replace the body of this function
    with a ``call_llm()`` invocation that asks the model to return a JSON
    mapping of new terms discovered during translation.

    Args:
        source_text: The original Spanish text.
        translated_text: The reviewed English translation (unused in the
            current heuristic implementation but accepted for API
            compatibility with future LLM-based implementations).
    """
    import logging as _logging

    logger = _logging.getLogger(__name__)
    glossary = load_terminology()

    # Extract emphasised phrases from the Spanish source
    emphasis_re = re.compile(r"\*{1,2}([^*\n]{2,40})\*{1,2}")
    spanish_candidates = sorted(
        {
            m.group(1).strip()
            for m in emphasis_re.finditer(source_text)
            if m.group(1).strip() not in glossary
        }
    )

    if spanish_candidates:
        logger.info(
            "Candidate terms for glossary review (not yet translated automatically): %s",
            ", ".join(spanish_candidates),
        )


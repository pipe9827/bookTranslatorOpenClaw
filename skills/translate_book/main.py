"""Translation pipeline for technical textbooks using an LLM.

This module orchestrates the full translation workflow:

1. Read ``.md`` source files from the ``input/`` directory.
2. Build a translation prompt using the template in ``prompts/translate.md``.
3. Call an LLM (abstracted via :func:`call_llm`) to produce a first-pass
   translation.
4. Build a review prompt using the template in ``prompts/review.md``.
5. Call the LLM again for an editorial review pass.
6. Save the final translation to ``output/``.
7. Update the terminology memory with any newly detected terms.

Usage::

    python main.py

Environment variables
---------------------
OPENAI_API_KEY : str, optional
    Required only when using the real OpenAI backend.  The default
    implementation is a no-op placeholder.
"""

import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------

SKILL_DIR = Path(__file__).parent
INPUT_DIR = SKILL_DIR / "input"
OUTPUT_DIR = SKILL_DIR / "output"
PROMPTS_DIR = SKILL_DIR / "prompts"
LOG_FILE = SKILL_DIR / "logs" / "execution.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Local imports (after path setup so relative imports resolve correctly)
# ---------------------------------------------------------------------------

from utils.file_manager import read_file, write_file  # noqa: E402
from utils.terminology import load_terminology, update_terminology  # noqa: E402

# ---------------------------------------------------------------------------
# LLM abstraction
# ---------------------------------------------------------------------------


def call_llm(prompt: str) -> str:
    """Send a prompt to the configured LLM and return the response.

    This is a **placeholder** implementation.  Replace the body with a real
    API call, for example::

        import openai
        client = openai.OpenAI()  # reads OPENAI_API_KEY from environment
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    Args:
        prompt: The full prompt string to send to the LLM.

    Returns:
        The model's text response.
    """
    # --- Replace this stub with a real LLM call ---
    logger.warning(
        "call_llm() is using the placeholder implementation. "
        "No actual API call was made."
    )
    return (
        "[PLACEHOLDER TRANSLATION — integrate a real LLM to obtain output]\n\n"
        + prompt[:200]
        + "\n..."
    )


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------


def _build_terminology_block(glossary: dict[str, str]) -> str:
    """Render the glossary as a Markdown table suitable for prompt injection.

    Args:
        glossary: Mapping of Spanish terms to English equivalents.

    Returns:
        A Markdown-formatted table string, or a placeholder message when the
        glossary is empty.
    """
    if not glossary:
        return "_No established terminology yet._"

    rows = ["| Spanish | English |", "|---------|---------|"]
    rows.extend(f"| {src} | {tgt} |" for src, tgt in glossary.items())
    return "\n".join(rows)


def build_translate_prompt(book_text: str, glossary: dict[str, str]) -> str:
    """Construct the translation prompt from the template.

    Args:
        book_text: Raw Markdown source text in Spanish.
        glossary: Current terminology glossary.

    Returns:
        The fully rendered prompt string ready to be sent to the LLM.

    Raises:
        FileNotFoundError: If ``prompts/translate.md`` does not exist.
    """
    template = read_file(PROMPTS_DIR / "translate.md")
    terminology_block = _build_terminology_block(glossary)
    prompt = template.replace("{{BOOK_TEXT}}", book_text)
    prompt = prompt.replace("{{TERMINOLOGY}}", terminology_block)
    return prompt


def build_review_prompt(translated_text: str, glossary: dict[str, str]) -> str:
    """Construct the review prompt from the template.

    Args:
        translated_text: First-pass English translation in Markdown format.
        glossary: Current terminology glossary.

    Returns:
        The fully rendered prompt string ready to be sent to the LLM.

    Raises:
        FileNotFoundError: If ``prompts/review.md`` does not exist.
    """
    template = read_file(PROMPTS_DIR / "review.md")
    terminology_block = _build_terminology_block(glossary)
    prompt = template.replace("{{TRANSLATED_TEXT}}", translated_text)
    prompt = prompt.replace("{{TERMINOLOGY}}", terminology_block)
    return prompt


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------


def translate_file(source_path: Path, glossary: dict[str, str]) -> str:
    """Run the two-pass translation pipeline for a single file.

    Pass 1 — Translation:
        Inject the source text into the translation prompt and call the LLM.

    Pass 2 — Review:
        Inject the first-pass translation into the review prompt and call the
        LLM to obtain the final, polished translation.

    Args:
        source_path: Path to the source ``.md`` file.
        glossary: Current terminology glossary (may be empty).

    Returns:
        The reviewed, final English translation as a string.

    Raises:
        OSError: If the source file cannot be read.
    """
    logger.info("Reading source file: %s", source_path)
    book_text = read_file(source_path)

    # --- Pass 1: Translation ---
    logger.info("Pass 1 — Translation: %s", source_path.name)
    translate_prompt = build_translate_prompt(book_text, glossary)
    translated_text = call_llm(translate_prompt)
    logger.info("Pass 1 complete for: %s", source_path.name)

    # --- Pass 2: Review ---
    logger.info("Pass 2 — Review: %s", source_path.name)
    review_prompt = build_review_prompt(translated_text, glossary)
    reviewed_text = call_llm(review_prompt)
    logger.info("Pass 2 complete for: %s", source_path.name)

    return reviewed_text


def run_pipeline() -> None:
    """Execute the translation pipeline for all ``.md`` files in ``input/``.

    For each file:

    * Translates and reviews the content.
    * Saves the result to ``output/<stem>_translated.md``.
    * Updates the terminology glossary.

    Errors for individual files are logged and do not abort the pipeline.
    """
    input_files = sorted(INPUT_DIR.glob("*.md"))
    if not input_files:
        logger.warning("No .md files found in %s — nothing to translate.", INPUT_DIR)
        return

    logger.info("Starting translation pipeline. Files to process: %d", len(input_files))

    glossary = load_terminology()
    logger.info("Loaded %d terminology entries.", len(glossary))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for source_path in input_files:
        try:
            reviewed_text = translate_file(source_path, glossary)

            output_filename = source_path.stem + "_translated.md"
            output_path = OUTPUT_DIR / output_filename
            write_file(output_path, reviewed_text)
            logger.info("Saved translation: %s", output_path)

            # Update terminology after each file so subsequent files benefit
            original_text = read_file(source_path)
            update_terminology(original_text, reviewed_text)
            # Reload glossary to pick up any newly added terms
            glossary = load_terminology()

        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to translate '%s': %s", source_path.name, exc, exc_info=True
            )

    logger.info("Pipeline finished.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_pipeline()

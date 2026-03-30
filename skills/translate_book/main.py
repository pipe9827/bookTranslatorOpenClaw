"""translate_book pipeline — main entry point.

Reads Markdown chapters from /input, translates them from Spanish to academic
British English using an LLM, performs a review pass, and saves the results to
/output.  A terminology glossary in /memory/terminology.md is maintained across
runs to ensure consistent translation of technical terms.
"""

import logging
import sys
from pathlib import Path

from utils.file_manager import read_file, write_file
from utils.terminology import load_terminology, update_terminology

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
PROMPTS_DIR = BASE_DIR / "prompts"
LOGS_DIR = BASE_DIR / "logs"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "execution.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LLM abstraction
# ---------------------------------------------------------------------------


def call_llm(prompt: str) -> str:
    """Send *prompt* to the configured LLM and return the response text.

    Replace the body of this function with your preferred LLM integration
    (e.g. OpenAI, Anthropic, a local model via Ollama, etc.).  The function
    must accept a plain-text prompt string and return a plain-text response.

    Example integration using the OpenAI Python SDK::

        import openai
        client = openai.OpenAI()  # reads OPENAI_API_KEY from the environment
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    Args:
        prompt: The fully rendered prompt to send to the LLM.

    Returns:
        The raw text returned by the LLM.

    Raises:
        NotImplementedError: Always, until a real integration is provided.
    """
    raise NotImplementedError(
        "call_llm() is a placeholder.  "
        "Implement LLM integration before running the pipeline."
    )


# ---------------------------------------------------------------------------
# Prompt rendering
# ---------------------------------------------------------------------------


def render_prompt(template: str, **variables: str) -> str:
    """Replace ``{{KEY}}`` placeholders in *template* with *variables*.

    Args:
        template: Prompt template text containing ``{{KEY}}`` placeholders.
        **variables: Keyword arguments whose names match the placeholder keys
            (case-sensitive, without the braces).

    Returns:
        The rendered prompt with all placeholders replaced.
    """
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------


def translate_text(book_text: str, translate_template: str, terminology: dict[str, str]) -> str:
    """Translate *book_text* using the translate prompt template.

    Args:
        book_text: Original Spanish Markdown text.
        translate_template: Contents of prompts/translate.md.
        terminology: Current glossary mapping Spanish terms to English.

    Returns:
        The translated English text as returned by the LLM.
    """
    glossary_block = _format_glossary(terminology)
    prompt = render_prompt(
        translate_template,
        BOOK_TEXT=book_text,
        TERMINOLOGY=glossary_block,
    )
    return call_llm(prompt)


def review_translation(
    original_text: str,
    translated_text: str,
    review_template: str,
    terminology: dict[str, str],
) -> str:
    """Run a review pass over *translated_text* to improve quality.

    Args:
        original_text: Original Spanish text (used as reference).
        translated_text: First-pass English translation.
        review_template: Contents of prompts/review.md.
        terminology: Current glossary mapping Spanish terms to English.

    Returns:
        The reviewed/corrected English text.
    """
    glossary_block = _format_glossary(terminology)
    prompt = render_prompt(
        review_template,
        BOOK_TEXT=original_text,
        TRANSLATED_TEXT=translated_text,
        TERMINOLOGY=glossary_block,
    )
    return call_llm(prompt)


def _format_glossary(terminology: dict[str, str]) -> str:
    """Format the terminology dictionary as a Markdown table string.

    Args:
        terminology: Mapping of Spanish terms to English equivalents.

    Returns:
        A Markdown-formatted table, or an empty string if the dict is empty.
    """
    if not terminology:
        return ""
    lines = ["| Spanish | English |", "|---------|---------|"]
    lines.extend(f"| {sp} | {en} |" for sp, en in sorted(terminology.items()))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_pipeline() -> None:
    """Execute the full translation pipeline.

    1. Load prompt templates.
    2. Load the terminology glossary.
    3. For each ``.md`` file in /input:
       a. Translate (first pass).
       b. Review (second pass).
       c. Save the final translation to /output.
       d. Update the terminology glossary.
    """
    # Load prompt templates
    translate_template = read_file(PROMPTS_DIR / "translate.md")
    review_template = read_file(PROMPTS_DIR / "review.md")

    # Collect input files
    input_files = sorted(INPUT_DIR.glob("*.md"))
    if not input_files:
        logger.warning("No .md files found in %s.  Nothing to process.", INPUT_DIR)
        return

    logger.info("Starting pipeline.  Files to process: %d", len(input_files))

    for md_file in input_files:
        logger.info("Processing: %s", md_file.name)
        try:
            # Load current glossary (may grow between files)
            terminology = load_terminology()

            # Read source content
            source_text = read_file(md_file)

            # --- Pass 1: translation ---
            translated_text = translate_text(source_text, translate_template, terminology)
            logger.info("  Translation pass complete for %s", md_file.name)

            # --- Pass 2: review ---
            reviewed_text = review_translation(
                source_text, translated_text, review_template, terminology
            )
            logger.info("  Review pass complete for %s", md_file.name)

            # Save output
            output_filename = md_file.stem + "_translated.md"
            output_path = OUTPUT_DIR / output_filename
            write_file(output_path, reviewed_text)
            logger.info("  Saved output to %s", output_path)

            # Update terminology glossary
            update_terminology(source_text, reviewed_text)
            logger.info("  Terminology glossary updated.")

        except NotImplementedError:
            logger.error(
                "call_llm() is not implemented.  "
                "Please provide an LLM integration before running the pipeline."
            )
            sys.exit(1)
        except Exception:
            logger.exception("Unexpected error while processing %s", md_file.name)

    logger.info("Pipeline finished.")


if __name__ == "__main__":
    run_pipeline()

# bookTranslatorOpenClaw

> An AI-powered translation pipeline for technical textbooks — Spanish → Academic British English.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [LLM Integration](#llm-integration)
- [Terminology Memory](#terminology-memory)
- [Logging](#logging)
- [Extending the Pipeline](#extending-the-pipeline)

---

## Overview

**bookTranslatorOpenClaw** translates technical textbook chapters written in
Spanish into academic British English.  The pipeline uses a two-pass LLM
approach:

1. **Translation pass** — converts the source Markdown into English while
   preserving structure, code blocks, and formatting.
2. **Review pass** — applies academic-style editing, enforces British spelling,
   and ensures terminology consistency.

A shared glossary in `skills/translate_book/memory/terminology.md` is loaded
before each file and updated after each file, so later chapters benefit from
terms established in earlier ones.

---

## Project Structure

```
skills/
└── translate_book/
    ├── main.py                 # Pipeline entry point
    ├── skill.yaml              # Skill metadata and step definitions
    ├── prompts/
    │   ├── translate.md        # First-pass (translation) prompt template
    │   └── review.md           # Second-pass (review) prompt template
    ├── memory/
    │   └── terminology.md      # Bilingual glossary (Spanish → English)
    ├── utils/
    │   ├── file_manager.py     # read_file / write_file helpers
    │   └── terminology.py      # load_terminology / update_terminology
    ├── logs/
    │   └── execution.log       # Runtime log (auto-created)
    ├── input/
    │   └── chapter1.md         # Sample Spanish source file
    └── output/
        └── chapter1_translated.md  # Generated translation (after running)
README.md
.gitignore
```

---

## Requirements

- Python **3.10+** (uses `str | Path` union type hints)
- No third-party packages are required for the pipeline itself.
- An LLM provider SDK (e.g. `openai`) is needed only once you wire up a real
  backend inside `call_llm()`.

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/pipe9827/bookTranslatorOpenClaw.git
cd bookTranslatorOpenClaw

# 2. (Optional) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Place your Spanish .md files in the input directory
cp my_chapter.md skills/translate_book/input/

# 4. Run the pipeline
cd skills/translate_book
python main.py
```

Translated files are written to `skills/translate_book/output/` with the
suffix `_translated.md`.

---

## Configuration

| Setting | Where to change | Default |
|---------|-----------------|---------|
| Input directory | `SKILL_DIR / "input"` in `main.py` | `skills/translate_book/input/` |
| Output directory | `SKILL_DIR / "output"` in `main.py` | `skills/translate_book/output/` |
| Translation prompt | `skills/translate_book/prompts/translate.md` | Provided |
| Review prompt | `skills/translate_book/prompts/review.md` | Provided |
| Glossary file | `skills/translate_book/memory/terminology.md` | Provided |
| Log file | `SKILL_DIR / "logs" / "execution.log"` in `main.py` | Auto-created |

---

## LLM Integration

The function `call_llm(prompt: str) -> str` in `main.py` is intentionally left
as a **placeholder**.  To connect a real LLM, replace the stub body.

### OpenAI example

```python
import openai

def call_llm(prompt: str) -> str:
    client = openai.OpenAI()          # reads OPENAI_API_KEY from environment
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content
```

Set your API key via the environment — **never hardcode it**:

```bash
export OPENAI_API_KEY="sk-..."
```

---

## Terminology Memory

The file `skills/translate_book/memory/terminology.md` stores a Markdown table
of Spanish → English term mappings.

- The glossary is **loaded** before each translation run.
- After each file, the pipeline **scans** the translation output for
  parenthetical glosses (e.g. `red neuronal (neural network)`) and appends any
  new terms it discovers.
- You can also edit the file manually to add or correct entries.

---

## Logging

All pipeline events are logged to both the console and
`skills/translate_book/logs/execution.log`.

Log entries include:

- File discovery results
- Start and completion of each translation/review pass
- Errors (with full tracebacks)

---

## Extending the Pipeline

- **Add a language pair**: Adjust the prompt templates and the glossary.
- **Support other formats**: Extend `file_manager.py` to handle `.rst`, `.txt`,
  or `.html` files and convert them to/from Markdown as needed.
- **Parallelise**: Wrap `translate_file()` in `concurrent.futures.ThreadPoolExecutor`
  for faster processing of large batches.
- **Integrate with OpenClaw**: Import and call `run_pipeline()` from your
  OpenClaw workflow definition.


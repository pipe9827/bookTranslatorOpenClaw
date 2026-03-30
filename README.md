# bookTranslatorOpenClaw

> AI-powered pipeline for translating technical book chapters from Spanish to
> academic British English, with terminology consistency across chapters.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [LLM Integration](#llm-integration)
6. [Terminology Management](#terminology-management)
7. [Logging](#logging)
8. [Extending the Pipeline](#extending-the-pipeline)

---

## Project Structure

```
skills/
└── translate_book/
    ├── main.py                  # Pipeline entry point
    ├── skill.yaml               # Skill metadata and step definitions
    ├── prompts/
    │   ├── translate.md         # First-pass translation prompt
    │   └── review.md            # Second-pass review prompt
    ├── memory/
    │   └── terminology.md       # Spanish → English glossary (auto-updated)
    ├── utils/
    │   ├── file_manager.py      # read_file / write_file helpers
    │   └── terminology.py       # Glossary load / update helpers
    ├── logs/
    │   └── execution.log        # Runtime log (auto-created)
    ├── input/                   # Place .md chapter files here
    │   └── chapter1.md          # Example chapter (Spanish)
    └── output/                  # Translated files written here
```

---

## Prerequisites

- Python 3.11 or later
- An API key for your chosen LLM provider (OpenAI, Anthropic, etc.)

No third-party Python packages are required until you wire up the LLM
integration (see below).

---

## Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/pipe9827/bookTranslatorOpenClaw.git
   cd bookTranslatorOpenClaw
   ```

2. **Add your chapter files**

   Copy one or more Markdown files (`.md`) into `skills/translate_book/input/`.

3. **Implement `call_llm()`** (see [LLM Integration](#llm-integration) below).

4. **Run the pipeline**

   ```bash
   cd skills/translate_book
   python main.py
   ```

5. **Retrieve the output**

   Translated files are written to `skills/translate_book/output/` with the
   suffix `_translated.md`.

---

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Input directory | `main.py` → `INPUT_DIR` | `skills/translate_book/input` |
| Output directory | `main.py` → `OUTPUT_DIR` | `skills/translate_book/output` |
| Translate prompt | `prompts/translate.md` | *(see file)* |
| Review prompt | `prompts/review.md` | *(see file)* |
| Terminology glossary | `memory/terminology.md` | *(see file)* |
| Log file | `logs/execution.log` | auto-created |

---

## LLM Integration

Open `skills/translate_book/main.py` and replace the body of `call_llm()` with
your preferred provider.

### OpenAI example

```python
import openai

def call_llm(prompt: str) -> str:
    client = openai.OpenAI()          # reads OPENAI_API_KEY from environment
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

Set the environment variable before running:

```bash
export OPENAI_API_KEY="sk-..."
```

### Anthropic example

```python
import anthropic

def call_llm(prompt: str) -> str:
    client = anthropic.Anthropic()    # reads ANTHROPIC_API_KEY from environment
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
```

---

## Terminology Management

The file `memory/terminology.md` contains a Markdown table of Spanish → English
term mappings.  Before each translation pass the pipeline injects the current
glossary into the prompt so the LLM uses consistent terminology.

After each chapter is processed the pipeline attempts to detect new technical
terms (emphasised phrases) and appends them to the glossary automatically.

You can also edit `terminology.md` manually to add, correct, or remove entries.

---

## Logging

Runtime information is written to `logs/execution.log` and also printed to
`stdout`.  The log includes:

- The name of each file being processed.
- Confirmation of each pipeline step (translation, review, save, glossary
  update).
- Any errors encountered during processing.

---

## Extending the Pipeline

| Goal | Where to change |
|------|----------------|
| Change translation style | Edit `prompts/translate.md` |
| Improve review criteria | Edit `prompts/review.md` |
| Add a third LLM pass | Add a step in `main.py` → `run_pipeline()` |
| Support other file formats | Extend `utils/file_manager.py` |
| Persist glossary to a database | Extend `utils/terminology.py` |
| Integrate with OpenClaw | Implement `call_llm()` using the OpenClaw API |

# Review Prompt

You are a senior academic editor and technical reviewer. Your task is to review
and improve a machine-translated excerpt from a technical textbook that was
translated **from Spanish into academic British English**.

## Review Criteria

1. **Academic tone**: Ensure the language is formal, precise, and appropriate
   for a university-level textbook. Eliminate any colloquialisms or informal
   phrasing.
2. **British English**: Correct any American English spellings or conventions
   to their British equivalents.
3. **Markdown structure**: Verify that the Markdown structure is identical to
   the original. Do **not** add, remove, or reorder structural elements.
4. **Code blocks**: Do **not** alter any content inside fenced code blocks or
   inline code spans.
5. **Terminology consistency**: Replace any inconsistent term with the
   established glossary equivalent listed below.
6. **Clarity and fluency**: Improve sentence flow where the translation reads
   awkwardly, without changing the meaning.
7. **No additions**: Do not introduce new content, examples, or explanations.

## Established Glossary

{{TERMINOLOGY}}

## Original Translated Text

{{TRANSLATED_TEXT}}

## Output

Provide **only** the reviewed and corrected Markdown text. Do not include any
preamble, explanation, or metadata.

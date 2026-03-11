"""Extract electrochemical methodology details from article text using a local Ollama LLM."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama
from pydantic import ValidationError

from json_schemas.echem_schema import ElectrochemicalMethodology

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ExtractionError(Exception):
    """Raised when the LLM output fails Pydantic validation after all retries."""

    def __init__(self, message: str, raw: str) -> None:
        super().__init__(message)
        self.raw = raw


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_NAME = "qwen3.5:4b"
MAX_RETRIES = 3
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "extract_echem_method.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_prompt_template(path: Path) -> str:
    """Return the raw prompt template string."""
    with open(path) as fh:
        return fh.read().strip()


def load_article_text(path: Path) -> str:
    """Return the content of a markdown article file."""
    with open(path) as fh:
        return fh.read().strip()


def build_llm() -> ChatOllama:
    """Instantiate the ChatOllama model with JSON-schema-constrained output."""
    return ChatOllama(
        model=MODEL_NAME,
        temperature=0,
        format=ElectrochemicalMethodology.model_json_schema(),
        reasoning=False,
        num_ctx=16384,
    )


def extract(article_text: str, llm: ChatOllama, prompt_template: str) -> ElectrochemicalMethodology:
    """
    Run the LLM extraction with up to MAX_RETRIES attempts.

    On a Pydantic ValidationError the raw LLM output and the error message are
    fed back to the model so it can self-correct.
    """
    initial_prompt = prompt_template.replace("{article_text}", article_text)
    messages: list = [HumanMessage(content=initial_prompt)]

    for attempt in range(1, MAX_RETRIES + 1):
        response = llm.invoke(messages)
        raw: str = response.content

        try:
            result = ElectrochemicalMethodology.model_validate_json(raw)
            if attempt > 1:
                print(f"  Validation succeeded on attempt {attempt}.")
            return result
        except ValidationError as exc:
            print(f"  Attempt {attempt}/{MAX_RETRIES} failed validation:\n{exc}")
            if attempt == MAX_RETRIES:
                raise ExtractionError(
                    f"Extraction failed after {MAX_RETRIES} attempts. "
                    f"Last validation error:\n{exc}",
                    raw=raw,
                ) from exc

            # Append the failed response and an error-correction request
            messages.append(AIMessage(content=raw))
            messages.append(
                HumanMessage(
                    content=(
                        "The JSON you returned failed schema validation with the following errors:\n\n"
                        f"{exc}\n\n"
                        "Please correct the issues and return a valid JSON object that conforms "
                        "exactly to the required schema. Return only the JSON object."
                    )
                )
            )

    # Should never be reached
    raise RuntimeError("Extraction failed unexpectedly.")


def process_file(article_path: Path, save_dir: Path, llm: ChatOllama, prompt_template: str) -> None:
    """Extract data from one article file and save to JSON."""
    print(f"Processing: {article_path.name}")
    article_text = load_article_text(article_path)

    out_path = save_dir / (article_path.stem + ".json")

    try:
        result = extract(article_text, llm, prompt_template)
        out_path.write_text(result.model_dump_json(indent=2))
        print(f"  Saved -> {out_path}")
    except ExtractionError as exc:
        print(f"  Validation failed: {exc}")
        try:
            parsed = json.loads(exc.raw)
            out_path.write_text(json.dumps(parsed, indent=2))
            print(f"  Saved (unvalidated JSON) -> {out_path}")
        except json.JSONDecodeError:
            print(f"  ERROR: Last output is not valid JSON, nothing saved.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Extract electrochemical methodology details from article markdown files "
            "using a local Ollama LLM and save structured JSON output."
        )
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        required=True,
        help="Directory containing input markdown (.md) article files.",
    )
    parser.add_argument(
        "--save_dir",
        type=Path,
        required=True,
        help="Directory where extracted JSON files will be saved.",
    )
    args = parser.parse_args()

    data_dir: Path = args.data_dir
    save_dir: Path = args.save_dir

    if not data_dir.is_dir():
        print(f"Error: data_dir '{data_dir}' is not a directory.")
        sys.exit(1)

    save_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(data_dir.glob("*.md"))
    if not md_files:
        print(f"No .md files found in '{data_dir}'.")
        sys.exit(0)

    print(f"Found {len(md_files)} file(s) to process.")
    prompt_template = load_prompt_template(PROMPT_PATH)
    llm = build_llm()

    for article_path in md_files:
        process_file(article_path, save_dir, llm, prompt_template)

    print("\nDone.")


if __name__ == "__main__":
    main()

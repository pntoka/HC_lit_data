'''Script to filter articles based on title and abstract using local LLM'''
import argparse
import os
import sys
from pathlib import Path

from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate

from get_abstract import get_abstract_and_title

MODEL_PATH = Path.home() / "llm_models" / "gemma-3-4b-it-Q4_K_M.gguf"
PROMPT_PATH = Path(__file__).parent / "prompt.md"


def load_prompt(prompt_path: Path) -> str:
    """Load the system prompt from a markdown file."""
    with open(prompt_path, "r") as f:
        return f.read().strip()


def load_dois(doi_file: Path) -> list[str]:
    """Read DOIs from a text file, one per line."""
    with open(doi_file, "r") as f:
        return [line.strip() for line in f if line.strip()]


def build_chain(system_prompt: str) -> tuple:
    """Initialise the LlamaCpp model and PromptTemplate chain."""
    llm = LlamaCpp(
        model_path=str(MODEL_PATH),
        n_gpu_layers=-1,
        temperature=0.0,
        max_tokens=4,
        verbose=False,
    )

    template = (
        f"{system_prompt}\n\n"
        "Title: {title}\n\n"
        "Abstract: {abstract}"
    )
    prompt = PromptTemplate(input_variables=["title", "abstract"], template=template)
    chain = prompt | llm
    return chain


def classify_doi(doi: str, chain, api_key: str) -> str | None:
    """Return 'yes', 'no', or None if abstract could not be retrieved."""
    abstract, title = get_abstract_and_title(doi, api_key)
    if abstract is None or title is None:
        print(f"  [SKIP] Could not retrieve abstract for {doi}")
        return None

    response = chain.invoke({"title": title, "abstract": abstract})
    return response.strip().lower()


def save_dois(dois: list[str], path: Path) -> None:
    """Write a list of DOIs to a text file, one per line."""
    with open(path, "w") as f:
        f.write("\n".join(dois) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Filter articles by relevance to hard carbon for sodium-ion batteries using a local LLM."
    )
    parser.add_argument("doi_file", type=Path, help="Path to a text file containing one DOI per line.")
    parser.add_argument("save_dir", type=Path, help="Directory where result files will be saved.")
    args = parser.parse_args()

    doi_file = args.doi_file
    save_dir = args.save_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("SCOPUS_API_KEY")
    if not api_key:
        print("Error: SCOPUS_API_KEY environment variable is not set.")
        sys.exit(1)

    system_prompt = load_prompt(PROMPT_PATH)
    dois = load_dois(doi_file)
    chain = build_chain(system_prompt)

    relevant = []
    not_relevant = []
    skipped = []

    for i, doi in enumerate(dois, 1):
        print(f"[{i}/{len(dois)}] {doi}")
        result = classify_doi(doi, chain, api_key)
        if result is None:
            skipped.append(doi)
        elif result == "yes":
            relevant.append(doi)
            print("  -> relevant")
        else:
            not_relevant.append(doi)
            print("  -> not relevant")

    save_dois(relevant, save_dir / "relevant.txt")
    save_dois(not_relevant, save_dir / "not_relevant.txt")
    if skipped:
        save_dois(skipped, save_dir / "skipped.txt")

    print(f"\nDone. Relevant: {len(relevant)}, Not relevant: {len(not_relevant)}, Skipped: {len(skipped)}")
    print(f"Results saved to {save_dir}")


if __name__ == "__main__":
    main()



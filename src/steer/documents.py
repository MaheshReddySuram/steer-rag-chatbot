from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentChunk:
    source: str
    title: str
    text: str


def load_policy_chunks(policy_dir: str | Path, max_words: int = 110) -> list[DocumentChunk]:
    """Load markdown policy files and split them into small retrievable chunks."""
    root = Path(policy_dir)
    chunks: list[DocumentChunk] = []

    for path in sorted(root.glob("*.md")):
        raw_text = path.read_text(encoding="utf-8").strip()
        if not raw_text:
            continue

        title = _extract_title(raw_text, path.stem.replace("_", " ").title())
        paragraphs = [part.strip() for part in raw_text.split("\n\n") if part.strip()]

        for index, paragraph in enumerate(paragraphs, start=1):
            for split_index, split_text in enumerate(_split_words(paragraph, max_words), start=1):
                chunks.append(
                    DocumentChunk(
                        source=f"{path.name}#chunk-{index}.{split_index}",
                        title=title,
                        text=split_text,
                    )
                )

    if not chunks:
        raise ValueError(f"No markdown policy documents found in {root}")

    return chunks


def _extract_title(text: str, fallback: str) -> str:
    first_line = text.splitlines()[0].strip()
    if first_line.startswith("#"):
        return first_line.lstrip("#").strip()
    return fallback


def _split_words(text: str, max_words: int) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]

    splits = []
    for start in range(0, len(words), max_words):
        splits.append(" ".join(words[start : start + max_words]))
    return splits

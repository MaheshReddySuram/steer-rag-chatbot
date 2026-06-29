from __future__ import annotations

from pathlib import Path

from .documents import load_policy_chunks
from .retriever import RetrievalResult, TfidfRetriever


class SteerChatbot:
    def __init__(self, policy_dir: str | Path = "data/policies") -> None:
        chunks = load_policy_chunks(policy_dir)
        self.retriever = TfidfRetriever(chunks)

    def answer(self, question: str, top_k: int = 3) -> dict:
        clean_question = question.strip()
        if not clean_question:
            return {
                "answer": "Please ask a question about the policy or support documents.",
                "sources": [],
            }

        results = self.retriever.search(clean_question, top_k=top_k)
        if not results:
            return {
                "answer": (
                    "I could not find a strong match in the available documents. "
                    "Try asking about refunds, escalation, account changes, or privacy requests."
                ),
                "sources": [],
            }

        return {
            "answer": self._compose_answer(clean_question, results),
            "sources": [
                {
                    "title": result.chunk.title,
                    "source": result.chunk.source,
                    "score": round(result.score, 3),
                    "text": result.chunk.text,
                }
                for result in results
            ],
        }

    def _compose_answer(self, question: str, results: list[RetrievalResult]) -> str:
        strongest = results[0].chunk.text
        source_title = results[0].chunk.title

        return (
            f"Here is the most relevant guidance I found: {strongest} "
            f"Source: {source_title}."
        )

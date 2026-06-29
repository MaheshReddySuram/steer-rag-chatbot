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
                "follow_up_questions": self._generic_follow_ups(),
                "sources": [],
            }

        results = self.retriever.search(clean_question, top_k=top_k)
        if not results:
            return {
                "answer": (
                    "I could not find a strong match in the available documents. "
                    "Try asking about refunds, escalation, account changes, or privacy requests."
                ),
                "follow_up_questions": self._generic_follow_ups(),
                "sources": [],
            }

        return {
            "answer": self._compose_answer(clean_question, results),
            "follow_up_questions": self._follow_ups_for_source(results[0].chunk.title),
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
        next_step = self._next_step_for_source(source_title)

        return (
            f"**Answer:** {strongest}\n\n"
            f"**Recommended next step:** {next_step}"
        )

    def _next_step_for_source(self, source_title: str) -> str:
        if source_title == "Refund Policy":
            return (
                "Confirm the order ID, customer email, purchase date, refund reason, "
                "and whether the refund is within the eligible window. If the amount is above "
                "500 dollars, send it to a support lead for review."
            )
        if source_title == "Support Escalation Policy":
            return (
                "Summarize the issue, attach the troubleshooting steps already completed, "
                "and route the case to the correct owner based on billing, security, or product impact."
            )
        if source_title == "Account Change Policy":
            return (
                "Verify the requestor identity before making the account change. For ownership "
                "or administrator changes, collect written approval from the current account owner."
            )
        if source_title == "Privacy Request Policy":
            return (
                "Verify the customer identity, log the request type and due date, and check whether "
                "legal retention review is needed before completing the request."
            )
        return "Review the cited policy passage and route the case to the correct support owner."

    def _follow_ups_for_source(self, source_title: str) -> list[str]:
        if source_title == "Refund Policy":
            return [
                "What details are required to validate a refund request?",
                "When should a refund case be escalated?",
                "What makes a refund request ineligible?",
            ]
        if source_title == "Support Escalation Policy":
            return [
                "Which team should own this escalated case?",
                "What details should be included before escalation?",
                "When is a case considered high priority?",
            ]
        if source_title == "Account Change Policy":
            return [
                "What identity checks are needed for account changes?",
                "When is written owner approval required?",
                "What should happen if an account change looks suspicious?",
            ]
        if source_title == "Privacy Request Policy":
            return [
                "What types of privacy requests can customers make?",
                "What needs to be logged for a privacy request?",
                "When should a privacy request be escalated?",
            ]
        return self._generic_follow_ups()

    def _generic_follow_ups(self) -> list[str]:
        return [
            "What policy should I check first?",
            "When should this case be escalated?",
            "What information should I collect from the customer?",
        ]

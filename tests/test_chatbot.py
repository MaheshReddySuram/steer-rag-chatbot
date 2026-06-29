from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from steer import SteerChatbot
from steer.documents import load_policy_chunks


def test_chatbot_returns_refund_source() -> None:
    bot = SteerChatbot(policy_dir=ROOT / "data" / "policies")
    response = bot.answer("What is the refund policy?")

    assert "answer" in response
    assert response["follow_up_questions"]
    assert response["sources"]
    assert any("Refund" in source["title"] for source in response["sources"])


def test_chatbot_handles_empty_question() -> None:
    bot = SteerChatbot(policy_dir=ROOT / "data" / "policies")
    response = bot.answer(" ")

    assert response["sources"] == []
    assert response["follow_up_questions"]
    assert "Please ask" in response["answer"]


def test_policy_headings_are_not_indexed_as_chunks() -> None:
    chunks = load_policy_chunks(ROOT / "data" / "policies")

    assert chunks
    assert all(not chunk.text.startswith("#") for chunk in chunks)


def test_refund_answer_includes_next_step_and_follow_ups() -> None:
    bot = SteerChatbot(policy_dir=ROOT / "data" / "policies")
    response = bot.answer("refund is not being credited to the account")

    assert "Recommended next step" in response["answer"]
    assert response["follow_up_questions"]
    assert response["follow_up_questions"][0].startswith("What details")

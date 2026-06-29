from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from steer import SteerChatbot


def test_chatbot_returns_refund_source() -> None:
    bot = SteerChatbot(policy_dir=ROOT / "data" / "policies")
    response = bot.answer("What is the refund policy?")

    assert "answer" in response
    assert response["sources"]
    assert any("Refund" in source["title"] for source in response["sources"])


def test_chatbot_handles_empty_question() -> None:
    bot = SteerChatbot(policy_dir=ROOT / "data" / "policies")
    response = bot.answer(" ")

    assert response["sources"] == []
    assert "Please ask" in response["answer"]

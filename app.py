from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "src"))

from steer import SteerChatbot


@st.cache_resource
def load_bot() -> SteerChatbot:
    return SteerChatbot(policy_dir=ROOT / "data" / "policies")


st.set_page_config(page_title="Steer", page_icon="S", layout="wide")

st.title("Steer")
st.caption("A RAG-powered chatbot for policies, FAQs, and support documents.")

bot = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me about refunds, support escalation, account changes, or privacy requests.",
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask a policy question")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    response = bot.answer(question)
    st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

    with st.chat_message("assistant"):
        st.write(response["answer"])
        if response["sources"]:
            st.subheader("Sources")
            for source in response["sources"]:
                with st.expander(f"{source['title']} - {source['source']}"):
                    st.write(source["text"])
                    st.caption(f"Similarity score: {source['score']}")

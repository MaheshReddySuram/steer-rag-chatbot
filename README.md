# Steer

Steer is a public-safe RAG chatbot that helps users navigate company policies, FAQs, and support documents with grounded answers and source references.

The project is intentionally generic: it uses synthetic sample policy documents and does not include any client, employer, or private data.

## What It Does

- Answers natural-language questions over policy and support documents
- Retrieves the most relevant document chunks before generating a response
- Shows source references so users can verify the answer
- Provides a Streamlit chatbot UI for demos
- Provides a static GitHub Pages chat demo at `/chat/`
- Exposes a FastAPI endpoint for backend integration
- Runs without an external LLM API key by using a local retrieval-first response engine

## Example Questions

- What is the refund policy?
- When should a support case be escalated?
- What information is required before approving an account change?
- How are data privacy requests handled?

## Architecture

```text
User Question
     |
     v
Streamlit UI / FastAPI
     |
     v
Document Loader -> Chunking -> TF-IDF Retrieval
     |
     v
Top Matching Policy Passages
     |
     v
Grounded Chatbot Response + Sources
```

## Tech Stack

- Python
- Streamlit
- FastAPI
- scikit-learn
- Pandas
- Pydantic
- Local policy document retrieval

## Project Structure

```text
steer-rag-chatbot/
  app.py
  api.py
  data/policies/
  src/steer/
  tests/
  requirements.txt
```

## Quick Start

Static GitHub Pages version:

```text
https://maheshreddysuram.github.io/steer-rag-chatbot/chat/
```

Python Streamlit version:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

For the API:

```bash
uvicorn api:app --reload
```

Then call:

```bash
POST http://127.0.0.1:8000/chat
```

Example body:

```json
{
  "question": "When should a customer support case be escalated?"
}
```

## Why This Project

Many teams have valuable information locked inside policies, FAQs, onboarding guides, and support playbooks. Steer demonstrates how retrieval-augmented generation concepts can help users find grounded answers quickly while still showing the source context behind each answer.

## Portfolio Talking Point

I built Steer as a public RAG chatbot project to demonstrate document ingestion, retrieval, grounded answer generation, source attribution, and API/UI delivery. The same pattern can be adapted to internal knowledge bases, customer support, compliance documents, fraud policies, healthcare guidelines, or operations playbooks.

## Disclaimer

This repository uses synthetic sample documents. It is for learning and portfolio demonstration only.

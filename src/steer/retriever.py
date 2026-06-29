from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .documents import DocumentChunk


@dataclass(frozen=True)
class RetrievalResult:
    chunk: DocumentChunk
    score: float


class TfidfRetriever:
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([chunk.text for chunk in chunks])

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            RetrievalResult(chunk=self.chunks[index], score=float(scores[index]))
            for index in top_indices
            if scores[index] > 0
        ]

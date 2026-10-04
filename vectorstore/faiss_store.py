from typing import TypedDict
import faiss

from embeddings.embedding_service import EmbeddingService
from models.schemas import DocumentChunk


class SearchResult(TypedDict):
    chunk: DocumentChunk
    score: float


class FAISSVectorStore:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.index = None

        self.chunks: list[DocumentChunk] = []

    def build_index(
        self,
        chunks: list[DocumentChunk]
    ):

        if not chunks:
            raise ValueError(
                "Cannot build vector index without chunks."
            )

        self.chunks = chunks

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service.embed_texts(texts)
        )

        dimension = embeddings.shape[1]

        # Inner product works like cosine similarity
        # because embeddings are normalized.
        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(
            embeddings
        )

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> list[SearchResult]:

        if self.index is None:
            raise ValueError(
                "Vector index has not been built."
            )

        if not query.strip():
            return []

        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        number_of_results = min(
            top_k,
            len(self.chunks)
        )

        scores, indices = self.index.search(
            query_embedding,
            number_of_results
        )

        results: list[SearchResult] = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            results.append(
                {
                    "chunk": self.chunks[index],
                    "score": float(score)
                }
            )

        return results
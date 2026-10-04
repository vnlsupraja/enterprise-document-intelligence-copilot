from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:

    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"

        self.model = SentenceTransformer(
            self.model_name
        )

    def embed_texts(
        self,
        texts: list[str]
    ) -> np.ndarray:

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings.astype("float32")

    def embed_query(
        self,
        query: str
    ) -> np.ndarray:

        embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.astype("float32")
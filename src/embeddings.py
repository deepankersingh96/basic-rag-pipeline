import openai
from typing import Iterable, Optional
from dotenv import load_dotenv

from src.models import Embedding, Chunk, Query


class Embedder:
    def __init__(self):
        load_dotenv()
        self.client = openai.Client()

    def embed_chunks(self, chunks: Iterable[Chunk]) -> Iterable[Embedding]:
        chunks = list(chunks) # materialize

        responses = self.client.embeddings.create(
            model="text-embedding-3-small", input=[chunk.text for chunk in chunks]
        )

        vectors = [x.embedding for x in responses.data]

        embeddings = [
            Embedding(chunk=chunk, vector=vector)
            for chunk, vector in zip(chunks, vectors)
        ]

        return embeddings

    def embed_queries(self, queries: Iterable[Query]) -> Iterable[Embedding]:
        queries = list(queries) # materialize

        responses = self.client.embeddings.create(
            model="text-embedding-3-small", input=[q.text for q in queries]
        )

        vectors = [x.embedding for x in responses.data]

        embeddings = [
            Embedding(
                query=Query(q_id=q.q_id, text=q.text, metadata=q.metadata), vector=vector
            )
            for q, vector in zip(queries, vectors)
        ]

        return embeddings

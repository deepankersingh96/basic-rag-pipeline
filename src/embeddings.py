import openai
from src.chunking import Chunk
from src.data import Document, Query
from typing import Iterable, Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Embedding:
    chunk: Chunk
    vector: list[float]


class Embedder:
    def __init__(self):
        load_dotenv()
        self.client = openai.Client()

    def embed_chunks(self, chunks: Iterable[Chunk]) -> Iterable[Embedding]:

        responses = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=[chunk.text for chunk in chunks]
        )

        vectors = [x.embedding for x in responses.data]

        embeddings = [Embedding(
            chunk=chunk,
            vector=vector
        ) for chunk, vector in zip(chunks, vectors)]

        return embeddings

    def embed_queries(self, queries: Iterable[Query]) -> Iterable[Embedding]:
        #TODO: EMbeddigns should not depend on Chunk or Document
        responses = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[q.text for q in queries]
                )

        vectors = [x.embedding for x in responses.data]
        
        embeddings = [Embedding(
            chunk=Chunk(
                id=q.id,
                doc_id=None,
                text=q.text,
                metadata=q.metadata
            ),
            vector=vector
        ) for q, vector in zip(queries, vectors)]

        return embeddings
import openai
from typing import Iterable, Protocol, runtime_checkable, ClassVar
from dotenv import load_dotenv

from .models import EmbeddedChunk, EmbeddedQuery, Chunk, Query


@runtime_checkable
class Embedder(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
    def embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]: ...
    def embed_queries(self, queries: list[Query]) -> list[EmbeddedQuery]: ...


class EmbedderFactory:
    _registry: ClassVar[dict[str, type[Embedder]]]= {}

    @classmethod
    def register(cls, name: str):
        def decorator(embedder_class: type[Embedder]):
            cls._registry[name] = embedder_class
            return embedder_class

        return decorator

    @classmethod
    def create(cls, name: str, *args, **kwargs):
        if name not in cls._registry.keys():
            raise ValueError(f"{name} not a valid embedder. \
                    Available embedders are {list(cls._registry.keys())}")
        embedder = cls._registry[name]
        return embedder(*args, **kwargs)


@EmbedderFactory.register("openai")
class OpenAIEmbedder:
    def __init__(self, model="text-embedding-3-small"):
        load_dotenv()
        self.client = openai.Client()
        self.model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        responses = self.client.embeddings.create(
            model=self.model, input=texts
        )
        vectors = [x.embedding for x in responses.data]
        return vectors

    def embed_chunks(self, chunks: Iterable[Chunk]) -> Iterable[EmbeddedChunk]:
        chunks = list(chunks)  # materialize

        vectors = self.embed_texts([chunk.text for chunk in chunks])

        embedded_chunks = [
            EmbeddedChunk(chunk=chunk, vector=vector)
            for chunk, vector in zip(chunks, vectors)
        ]
        return embedded_chunks

    def embed_queries(self, queries: Iterable[Query]) -> Iterable[EmbeddedQuery]:
        queries = list(queries)  # materialize

        vectors = self.embed_texts([query.text for query in queries])

        embedded_queries = [
            EmbeddedQuery(query=q, vector=vector) for q, vector in zip(queries, vectors)
        ]
        return embedded_queries

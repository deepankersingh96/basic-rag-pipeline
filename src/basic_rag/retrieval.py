from collections.abc import Iterable
from typing import ClassVar, Protocol

import pyarrow as pa
import pyarrow.compute as pc
import lancedb

from .models import EmbeddedQuery


class Retriever(Protocol):
    def setup(self, vector_db_uri: str, vector_db_name: str): ...
    def search_query(self, embedded_query: type[EmbeddedQuery]): ...


class RetrieverFactory:
    _registry = ClassVar[dict[str, type[Retriever]]]

    @classmethod
    def register(cls, name: str):
        def decorator(retriever_cls: type[Retriever]):
            cls._registry[name] = retriever_cls
            return retriever_cls

        return decorator

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> type[Retriever]:
        if name not in cls._registry.keys():
            raise ValueError(f"{name} not a valid Retriever type.")
        retriever_cls = cls._registry[name]
        return retriever_cls(*args, **kwargs)


@RetrieverFactory.register("lancedb")
class LanceDBRetriever:
    def __init__(self):
        self.db = None
        self.table = None

    def setup(self, vector_db_uri: str, vector_db_name: str):
        self.table = lancedb.connect(vector_db_uri).open_table(vector_db_name)

    def search_query(self, embedded_query: type[EmbeddedQuery], **kwargs):
        emb = embedded_query

        result = (
            self.table.search(emb.vector, vector_column_name="vector")
            .metric(kwargs.metric)
            .limit(kwargs.limit)
            .to_arrow()
        )
        result = result.append_column("q_id", pa.array([emb.query.q_id] * len(result)))
        result = result.append_column("score_retrieval", pc.negate(result["_distance"]))

        return result

    def search_queries(
        self, q_embeddings: Iterable[EmbeddedQuery], **kwargs
    ) -> type[pa.Table]:
        q_embeddings = list(q_embeddings)
        results = []

        for emb in q_embeddings:
            results.append(self.search_query(emb, **kwargs))

        return pa.concat_tables(results) if results else pa.table({})

import lancedb
from .models import EmbeddedChunk
from typing import Protocol, ClassVar
import pyarrow as pa
import json

schema = pa.schema(
    [
        pa.field("ch_id", pa.string(), nullable=False),
        pa.field("doc_id", pa.string(), nullable=False),
        pa.field("text", pa.string(), nullable=True),
        pa.field("metadata", pa.string(), nullable=True),
        pa.field(
            "vector", pa.list_(pa.float32(), 1536), nullable=False
        ),  # Fixes the 'None' vector issue
    ]
)


class VectorDB(Protocol):
    def create_db(self, name: str, uri: str): ...
    def get_db(self): ...
    def add_to_db(self, embedded_chunks: list[EmbeddedChunk]): ...
    def index_db(self, index_type: str, **kwargs): ...  # Creates index from scratch
    def update_index(self): ...  # Optimize the index incrementally


class VectorDBFactory:
    _registry = ClassVar[dict[str, type[VectorDB]]]

    @classmethod
    def register(cls, name: str):
        def decorator(vector_db_cls: type[VectorDB]):
            cls._registry[name] = vector_db_cls
            return vector_db_cls

        return decorator

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> type[VectorDB]:
        if name not in cls._registry.keys():
            raise ValueError(f"{name} not a valid VectorDB type.")
        vector_db_cls = cls._registry[name]
        return vector_db_cls(*args, **kwargs)


@VectorDBFactory.register("lancedb")
class LanceDBIndexer:
    def __init__(self):
        # self.db = None
        self.table = None

    def create_db(self, name: str, uri: str):
        if self.table is not None:
            raise ValueError("Class object already has an associated VectorDB.")
        table_name = name
        self.table = lancedb.connect(uri).create_table(
            table_name, schema=schema, mode="overwrite"
        )

    def get_db(self):
        return self.table

    def add_to_db(self, embedded_chunks: list[EmbeddedChunk]):
        data_to_insert = [
            {
                "ch_id": emb.chunk.ch_id,
                "doc_id": emb.chunk.doc_id,
                "text": emb.chunk.text,
                "metadata": json.dumps(emb.chunk.metadata),
                "vector": emb.vector,
            }
            for emb in embedded_chunks
        ]
        self.table.add(data_to_insert)

    def index_db(self, index_type: str, **kwargs):
        self.table.create_index(index_type=index_type, **kwargs)

    def update_index(self):
        self.table.optimize()

from typing import Protocol, ClassVar, runtime_checkable
import logging

import lancedb
import pyarrow as pa
import json

from .models import EmbeddedChunk

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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


@runtime_checkable
class VectorDB(Protocol):
    def create_db(self, name: str, uri: str): ...
    def get_db(self): ...
    def add_to_db(self, embedded_chunks: list[EmbeddedChunk]): ...
    def index_db(self, index_type: str, **kwargs): ...  # Creates index from scratch
    def update_index(self): ...  # Optimize the index incrementally


class VectorDBFactory:
    _registry: ClassVar[dict[str, type[VectorDB]]] = {}

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
class LanceVectorDB:
    def __init__(self, db_name: str, db_uri: str, load_existing: bool = False):
        self.table = None
        self.create_db(name=db_name, uri=db_uri, load_existing=load_existing)

    def create_db(self, name: str, uri: str, load_existing: bool):
        table_name = name
        connection = lancedb.connect(uri)

        if load_existing and table_name in connection.list_tables().tables:
            self.table = connection.open_table(table_name)
            logger.info(f"LOADED EXISTING TABLE: {table_name}")
        else:
            self.table = connection.create_table(
                table_name, schema=schema, mode="overwrite"
            )
            logger.info(f"CREATED NEW TABLE: {table_name}")

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
        logger.info(f"Created DB Index. Index type={index_type}")
        self.table.create_index(index_type=index_type, **kwargs)

    def update_index(self):
        self.table.optimize()

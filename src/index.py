import lancedb
from src.models import Embedding, Chunk
from typing import Iterable, Literal
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


class Indexer:
    def __init__(
        self, uri, table_name, mode: Literal["overwrite", "append"] = "append"
    ):
        self.db = lancedb.connect(uri)
        if mode == "overwrite" or table_name not in self.db.table_names():
            self.table = self.db.create_table(
                table_name, None, schema=schema, mode="overwrite"
            )
        else:
            self.table = self.db.open_table(table_name)

    def get_index(self):
        return self.db

    def add_to_index(self, embeddings: Iterable[Embedding]):

        data_to_insert = [
            {
                "ch_id": emb.chunk.ch_id,
                "doc_id": emb.chunk.doc_id,
                "text": emb.chunk.text,
                "metadata": json.dumps(emb.chunk.metadata),
                "vector": emb.vector,
            }
            for emb in embeddings
        ]

        self.table.add(data_to_insert)

        return

    def search(self, q_embeddings, top_k=10):
        q_embeddings = list(
            q_embeddings
        )  # materialize the iterator, to prevent loading next batch.
        tables = []

        for emb in q_embeddings:
            result = (
                self.table.search(emb.vector, vector_column_name="vector")
                .metric("cosine")
                .limit(top_k)
                .to_arrow()
            )

            result = result.append_column(
                "q_id", pa.array([emb.query.q_id] * len(result))
            )
            tables.append(result)

        return pa.concat_tables(tables) if tables else pa.table({})

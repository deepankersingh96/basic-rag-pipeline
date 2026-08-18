import lancedb
from src.embeddings import Embedding
from src.chunking import Chunk
from typing import Iterable, Optional
import pyarrow as pa
import json 
from dataclasses import dataclass


@dataclass
class Retreival:
    chunk: Chunk
    distance: float


schema = pa.schema([
    pa.field("id", pa.string(), nullable=False),
    pa.field("doc_id", pa.string(), nullable=False),
    pa.field("text", pa.string(), nullable=True),
    pa.field("metadata", pa.string(), nullable=True),
    pa.field("vector", pa.list_(pa.float32(), 1536), nullable=False) # Fixes the 'None' vector issue
])

class Indexer:
    def __init__(self, uri, table_name):
        self.db = lancedb.connect(uri)
        if table_name not in self.db.table_names():
            self.table = self.db.create_table(table_name, None, schema=schema, mode='overwrite')
        else:
            self.table = self.db.open_table(table_name)
    def get_index(self):
        return self.db

    def add_to_index(self, embeddings:Iterable[Embedding]):

        data_to_insert = [{
            "id": emb.chunk.id,
            "doc_id": emb.chunk.doc_id,
            "text": emb.chunk.text,
            "metadata": json.dumps(emb.chunk.metadata),
            "vector": emb.vector
        } for emb in embeddings]

        self.table.add(data_to_insert)

        return 

    def search(self, q_embeddings:Iterable[Embedding], top_k=10):
        # TODO: sync the qurey IDs with retrieved document IDs.
        results = self.table.search(
            [emb.vector for emb in q_embeddings],
            vector_column_name='vector', # search against the 'vector' col in table
        ).metric("cosine").limit(top_k).to_arrow()

        return results
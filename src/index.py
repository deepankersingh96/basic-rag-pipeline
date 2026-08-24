import lancedb
from src.models import Embedding
from typing import Iterable, Literal, TypeAlias, get_args
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

Mode: TypeAlias = Literal["overwrite", "append"]
VALID_MODES = get_args(Mode)


class Indexer:
    def __init__(
        self,
        uri,
    ):
        self.db = lancedb.connect(uri)

    def get_index(self):
        return self.db

    def get_table(self, dataset_name: str):
        return self.db.open_table(
            dataset_name
        )  # table name should be self explanatory -> dataset name + encoder + chunking

    def add_to_index(
        self,
        embeddings: Iterable[Embedding],
        dataset_name: str,
        mode: Mode = "append",
    ):

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
        if mode not in VALID_MODES:
            raise ValueError(
                f'Invalid mode {mode!r}. Valid values are: {", ".join(VALID_MODES)}'
            )

        if mode == "overwrite":
            self.db.create_table(name=dataset_name, data=data_to_insert, mode=mode)
        elif mode == "append":
            self.db.open_table(dataset_name).add(data_to_insert)

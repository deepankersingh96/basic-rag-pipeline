from collections.abc import Iterable
from typing import TypeAlias, Literal, get_args

import pyarrow as pa
import pyarrow.compute as pc
import lancedb

from src.reranking import Reranker


DIST_METRIC: TypeAlias = Literal["l2", "cosine", "dot"]
VALID_DIST_METRICS = get_args(DIST_METRIC)


class Retriever:
    def __init__(self, uri):
        self.db = lancedb.connect(uri)
        self.reranker = Reranker("cross-encoder/ms-marco-MiniLM-L6-v2")

    def search(
        self,
        *,
        dataset_name: str,
        q_embeddings: Iterable,
        dist_metric: DIST_METRIC,
        top_k: int = 10,
    ) -> pa.Table:
        db_table = self.db.open_table(dataset_name)
        q_embeddings = list(q_embeddings)
        tables = []

        if dist_metric not in VALID_DIST_METRICS:
            raise ValueError(
                f'{dist_metric} not a valid distance metric. Allowed values are {", ".join(VALID_DIST_METRICS)}'
            )

        for emb in q_embeddings:
            result = (
                db_table.search(emb.vector, vector_column_name="vector")
                .metric(dist_metric)
                .limit(top_k)
                .to_arrow()
            )

            result = result.append_column(
                "q_id", pa.array([emb.query.q_id] * len(result))
            )
            result = result.append_column(
                "score_retrieval", pc.negate(result["_distance"])
            )

            tables.append(result)

        return pa.concat_tables(tables) if tables else pa.table({})

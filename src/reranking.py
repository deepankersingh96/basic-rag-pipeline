from typing import Iterable

from sentence_transformers import CrossEncoder
import pyarrow as pa
import pyarrow.compute as pc

from src.models import Query, Embedding


class Reranker:
    def __init__(self, model_name: str):
        self.cross_encoder = CrossEncoder(
            model_name
        )  # "cross-encoder/ms-marco-MiniLM-L6-v2"

    def re_rank(self, query: Query, retrievals: pa.Table) -> pa.Table:
        retrievals = (
            retrievals.to_pandas()
        )  # TODO: can this be done without converting to pandas?

        cross_inp = [[query.text, doc_text] for doc_text in retrievals["text"]]

        cross_scores = self.cross_encoder.predict(cross_inp)

        retrievals["score_cross_enc"] = cross_scores

        return pa.Table.from_pandas(retrievals)

    def re_rank_batch(
        self, q_embeddings: Iterable[Embedding], batch_retrievals: pa.Table
    ) -> pa.Table:
        re_ranked_batch = []

        # re-rank each q_id with re_rank
        for q_emb in q_embeddings:
            query = q_emb.query
            filtered = batch_retrievals.filter(
                pc.equal(batch_retrievals["q_id"], query.q_id)
            )

            re_ranked_retrievals = self.re_rank(query, filtered)
            re_ranked_batch.append(re_ranked_retrievals)

        # gather results
        re_ranked_batch = pa.concat_tables(re_ranked_batch)

        # assign score to be re-ranker score.
        re_ranked_batch = re_ranked_batch.append_column(
            "score", re_ranked_batch["score_cross_enc"]
        )

        return re_ranked_batch


class NoOpReranker:
    def __init__(self):
        pass
    
    def re_rank_batch(
        self, q_embeddings: Iterable[Embedding], batch_retrievals: pa.Table
    ) -> pa.Table:

        # assign score to be retriever score.
        batch_retrievals = batch_retrievals.append_column(
            "score", batch_retrievals["score_retrieval"]
        )
        return batch_retrievals

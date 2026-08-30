from typing import Iterable, Protocol, runtime_checkable, ClassVar

from sentence_transformers import CrossEncoder
import pyarrow as pa
import pyarrow.compute as pc

from .models import Query, EmbeddedQuery


@runtime_checkable
class ReRanker(Protocol):
    def setup(self, **kwargs): ...
    def re_rank(self, query: type[Query], retrievals: type[pa.Table]): ...


class ReRankerFactory:
    _registry: ClassVar[dict[str, type[ReRanker]]]={}

    @classmethod
    def register(cls, name: str):
        def decorator(re_ranker_cls: type[ReRanker]):
            cls._registry[name] = re_ranker_cls
            return re_ranker_cls

        return decorator

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> type[ReRanker]:
        if name not in cls._registry.keys():
            raise ValueError(f"{name} not a valid Re-Ranker type.")
        re_ranker_cls = cls._registry[name]
        return re_ranker_cls(*args, **kwargs)


@ReRankerFactory.register("cross_encoder")
class CrossEncoderReRanker:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.cross_encoder = None
        self.setup()

    def setup(self):
        self.cross_encoder = CrossEncoder(
            self.model_name
        )  

    def re_rank(self, query: type[Query], retrievals: type[pa.Table]):
        # TODO: can this be done without converting to pandas?
        retrievals = retrievals.to_pandas()
        cross_inp = [[query.text, doc_text] for doc_text in retrievals["text"]]
        cross_scores = self.cross_encoder.predict(cross_inp)
        retrievals["score_cross_enc"] = cross_scores

        return pa.Table.from_pandas(retrievals)

    def re_rank_batch(
        self,
        embedded_queries: Iterable[EmbeddedQuery],
        batch_retrievals: type[pa.Table],
    ):
        re_ranked_batch = []

        # re-rank each q_id with re_rank
        for q_emb in embedded_queries:
            query = q_emb.query
            filtered_rets = batch_retrievals.filter(
                pc.equal(batch_retrievals["q_id"], query.q_id)
            )

            re_ranked_retrievals = self.re_rank(query, filtered_rets)
            re_ranked_batch.append(re_ranked_retrievals)

        # gather results
        re_ranked_batch = pa.concat_tables(re_ranked_batch)

        # assign score to be re-ranker score.
        re_ranked_batch = re_ranked_batch.append_column(
            "score", re_ranked_batch["score_cross_enc"]
        )

        return re_ranked_batch


@ReRankerFactory.register("no_op")
class NoOpReranker:
    def setup(self):
        pass

    def re_rank(self, query: type[Query], retrievals: type[pa.Table]):
        # assign score to be retriever score.
        retrievals = retrievals.append_column("score", retrievals["score_retrieval"])
        return retrievals

    def re_rank_batch(
        self, embedded_queries: Iterable[EmbeddedQuery], batch_retrievals: pa.Table
    ) -> pa.Table:

        # assign score to be retriever score.
        batch_retrievals = batch_retrievals.append_column(
            "score", batch_retrievals["score_retrieval"]
        )
        return batch_retrievals


@ReRankerFactory.register("llm")
class LLMReRanker: ...

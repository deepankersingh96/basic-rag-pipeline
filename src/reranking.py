from sentence_transformers import CrossEncoder
from src.models import Query
import pyarrow as pa


class Reranker:
    def __init__(self, model_name: str):
        self.cross_encoder = CrossEncoder(model_name) # "cross-encoder/ms-marco-MiniLM-L6-v2"

    def re_rank(self, query: Query, retrievals: pa.Table) -> pa.Table:
        retrievals = retrievals.to_pandas() # TODO: can this be done without converting to pandas?

        cross_inp = [[query.text, doc_text] for doc_text in retrievals['text']] 

        cross_scores = self.cross_encoder.predict(cross_inp)

        retrievals["score_cross_enc"] = cross_scores

        return pa.Table.from_pandas(retrievals)






import pytrec_eval
from collections import defaultdict
import pandas as pd


class Evaluator:
    def __init__(self):
        self.evaluator = None

    @staticmethod
    def df_to_pytrec(df: pd.DataFrame):
        run = defaultdict(dict)
        print(f"Converting {len(df)} queries.")

        for _id, doc_id, distance in df[["id", "doc_id", "_distance"]].itertuples(
            index=False
        ):
            run[_id][doc_id] = - distance

        print(f"Found {len(run)} run queries.")
        return run

    @staticmethod
    def parse_qrel(f_qrel, ignore_header=False):
        qrel = defaultdict(dict)
        header_ignored = False

        for line in f_qrel:
            if ignore_header and not header_ignored:
                header_ignored = True
                continue
            query_id, object_id, relevance = line.strip().split()

            assert object_id not in qrel[query_id]
            qrel[query_id][object_id] = int(relevance)

        print(f"Parsed {len(qrel)} qrels.")
        return qrel

    @staticmethod
    def print_line(measure, scope, value):
        print('{:25s}{:8s}{:.4f}'.format(measure, scope, value))

    def evaluate(self, qrel, run, measures):
        self.evaluator = pytrec_eval.RelevanceEvaluator(qrel, measures)
        results = self.evaluator.evaluate(run)

        for measure in measures:
            self.print_line(
                measure,
                'all',
                pytrec_eval.compute_aggregated_measure(
                    measure,
                    [query_measures[measure.replace('.', '_')]
                    for query_measures in results.values()]))
        
        return results

# Load data into Documents schema

from typing import Iterable
import jsonlines

from src.models import Document, Query


class BIERDataset:
    def __init__(self):
        pass

    def document_loader(self, file_path, batch_size=4) -> Iterable[Document]:
        batch = []

        with jsonlines.open(file_path, "r") as reader:
            for line in reader:
                document = Document(
                    doc_id=line["_id"],
                    text=line["title"] + " - " + line["text"],
                    metadata=line.get("metadata", {}),
                )
                batch.append(document)

                if len(batch) == batch_size:
                    yield batch
                    batch = []

            if batch:
                yield batch

    def query_loader(self, file_path, batch_size=4) -> Iterable[Query]:
        batch = []

        with jsonlines.open(file_path, "r") as reader:
            for line in reader:
                doc = Query(
                    q_id=line["_id"], text=line["text"], metadata=line["metadata"]
                )
                batch.append(doc)

                if len(batch) == batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

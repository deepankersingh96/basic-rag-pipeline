# Load data into Documents schema

from dataclasses import dataclass
from typing import Optional, Iterable
import jsonlines

@dataclass
class Document:
    id: str
    text: str
    metadata: Optional[dict]

@dataclass
class Query:
    id: str
    text: str
    metadata: Optional[dict]

class BIERDataset:
    def __init__(self):
        pass

    def document_loader(self, file_path, batch_size=4) -> Iterable[Document]:
        batch = []

        with jsonlines.open(file_path, 'r') as reader: 
            for line in reader:
                document = Document(
                    id=line['_id'],
                    text=line['title'] + ' - ' + line['text'],
                    metadata=line.get('metadata', {})
                )
                batch.append(document)

                if len(batch) == batch_size:
                    yield batch
                    batch = []

            if batch:
                yield batch

    def query_loader(self, file_path, batch_size=4) -> Iterable[Query]:
        batch = []

        with jsonlines.open(file_path, 'r') as reader:
            for line in reader:
                doc = Query(
                    id=line['_id'], 
                    text=line['text'],
                    metadata=line['metadata']
                )
                batch.append(doc)

                if len(batch) == batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch
    




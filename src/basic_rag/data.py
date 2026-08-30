# Load data into Documents schema

from typing import Iterable, ClassVar, Protocol
import jsonlines
from pprint import pprint

from .models import Document, Query


class IRDataset(Protocol):
    def document_loader(self, file_path: str, batch_size: int) -> Iterable[Document]:
        pass

    def query_loader(self, file_path, batch_size=4) -> Iterable[Query]:
        pass


class DatasetFactory:
    _registry: ClassVar[dict[str, type[IRDataset]]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(dataset_cls: type[IRDataset]):
            cls._registry[name] = dataset_cls
            return dataset_cls

        return decorator

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> type[IRDataset]:
        if name not in cls._registry.keys():
            raise ValueError(f"""{name} is not an available dataset type. 
                Available datasets are {list(cls._registry.keys())}""")
        return cls._registry[name](*args, **kwargs)


@DatasetFactory.register("beir")
class BIERDataset:
    def __init__(self):
        pass

    def document_loader(
        self, file_path: str, batch_size: int = 4
    ) -> Iterable[Document]:
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


if __name__ == "__main__":
    beir_loader = DatasetFactory.create("beir").document_loader(
        file_path="datasets/beir/datasets/scifact/corpus.jsonl"
    )

    batch = next(beir_loader)

    print(f"Loaded batch with size={len(batch)}")
    pprint(f"First batch element: \n{batch[0]}")

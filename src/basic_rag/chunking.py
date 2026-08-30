from typing import Iterable, ClassVar
from abc import ABC, abstractmethod
from llama_index.core.node_parser import SentenceSplitter, TokenTextSplitter
import tiktoken

from .models import Document, Chunk

__all__ = ["WordChunker", "TokenChunker", "SentenceChunker"]


class Chunker(ABC):
    @abstractmethod
    def chunk(self, documents: Iterable[Document]) -> Iterable[Chunk]: ...


class ChunkerFactory:
    _registry: ClassVar[dict[str, type[Chunker]]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(chunker_cls: type[Chunker]):
            cls._registry[name] = chunker_cls
            return chunker_cls
        return decorator

    @classmethod
    def create(cls, name:str, **kwargs):
        if name not in cls._registry.keys():
            raise ValueError(f"{name} not a valid chunker name.")
        return cls._registry[name](**kwargs)


@ChunkerFactory.register("token")
class TokenChunker(Chunker):
    def __init__(
        self, chunk_size: int = 512, chunk_overlap: int = 50, encoding: str = "gpt-4o"
    ):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = encoding

    def chunk(self, documents: Iterable[Document]) -> Iterable[Chunk]:
        chunks = []
        encoding = tiktoken.encoding_for_model("gpt-4o")

        for doc in documents:
            text = doc.text
            tokens = encoding.encode(text)

            for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
                chunks.append(
                    Chunk(
                        ch_id=f"{doc.doc_id}_{i}",
                        doc_id=doc.doc_id,
                        text=encoding.decode(
                            tokens[
                                i : min(
                                    i + self.chunk_size,
                                    len(tokens),
                                )
                            ]
                        ),
                        metadata=doc.metadata,
                    )
                )

        return chunks


@ChunkerFactory.register("word")
class WordChunker(Chunker):
    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 50,
    ):
        super().__init__()
        self.splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
        )

    def chunk(self, documents):
        chunks = []

        for doc in documents:
            splits = self.splitter.split_text(doc.text)
            for split_id, split in enumerate(splits):
                chunks.append(
                    Chunk(
                        ch_id=f"{doc.doc_id}_{split_id}",
                        doc_id=doc.doc_id,
                        text=split,
                        metadata=doc.metadata,
                    )
                )

        return chunks


@ChunkerFactory.register("sentence")
class SentenceChunker(Chunker):
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        paragraph_separator: str = "\n\n",
        secondary_chunking_regex: str = None,
    ):
        super().__init__()
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paragraph_separator=paragraph_separator,
            secondary_chunking_regex=secondary_chunking_regex,
        )

    def chunk(self, documents):
        chunks = []

        for doc in documents:
            splits = self.splitter.split_text(doc.text)
            for split_id, split in enumerate(splits):
                chunks.append(
                    Chunk(
                        ch_id=f"{doc.doc_id}_{split_id}",
                        doc_id=doc.doc_id,
                        text=split,
                        metadata=doc.metadata,
                    )
                )

        return chunks

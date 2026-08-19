from dataclasses import dataclass
from typing import Optional, Iterable
import jsonlines

from src.models import Document, Chunk


class Chunker:
    def __init__(self):
        pass

    def split_fix_size(self, text, size):
        chunks = []
        chunk = []
        for word in text.split(" "):
            chunk.append(word)
            if len(chunk) == size:
                chunks.append(" ".join(chunk))
                chunk = []
        if chunk:
            chunks.append(" ".join(chunk))

        return chunks

    def fixed_size_chunking(
        self, documents: Iterable[Document], chunk_size: int
    ) -> Iterable[Chunk]:
        chunks = []

        for doc in documents:
            text = doc.text
            splits = self.split_fix_size(text, chunk_size)

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

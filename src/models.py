from dataclasses import dataclass
from typing import Optional


@dataclass
class Document:
    doc_id: str
    text: str
    metadata: Optional[dict]

@dataclass
class Query:
    q_id: str
    text: str
    metadata: Optional[dict]

@dataclass
class Chunk:
    ch_id: str
    doc_id: str
    text: str
    metadata: Optional[dict]

@dataclass
class Embedding:
    vector: list[float]
    chunk: Optional[Chunk] = None
    query: Optional[Query] = None

@dataclass
class Retreival:
    chunk: Chunk
    distance: float
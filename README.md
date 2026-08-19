# Basic RAG Pipeline

SciFact-first retrieval pipeline for experimenting with chunking, embeddings, LanceDB indexing, and evaluation on BEIR-style datasets.

The current end-to-end example lives in [`notebooks/scifact_ir.ipynb`](./notebooks/scifact_ir.ipynb).

## Overview

This project loads BEIR data, chunks documents, embeds chunks and queries, stores document embeddings in a vector database, retrieves the nearest matches for each query, and evaluates the results.

At the moment, the implementation is centered on the SciFact dataset. The rest of BEIR is a planned expansion.

## Quick Start

1. Download the BEIR datasets first:

   ```bash
   python datasets/beir/download.py
   ```

2. Open [`notebooks/scifact_ir.ipynb`](./notebooks/scifact_ir.ipynb).
3. Load the SciFact corpus and queries.
4. Chunk documents using the current fixed-size chunker.
5. Generate embeddings.
6. Insert document embeddings into LanceDB.
7. Run retrieval and evaluation.

The notebook is the canonical usage path for now, so it is the best place to see the project run end to end.

## Project Structure

```text
basic-rag-pipeline/
├── README.md
├── pyproject.toml
├── uv.lock
├── notebooks/
│   ├── scifact_ir.ipynb
│   ├── ir_beir.ipynb
│   └── rag-cat-facts.ipynb
└── src/
    ├── __init__.py
    ├── chunking.py
    ├── data.py
    ├── embeddings.py
    ├── evaluation.py
    ├── index.py
    ├── models.py
    └── retrieval.py
```

## Current Features

- SciFact dataset support through the notebook workflow.
- Document loading from BEIR-style JSONL files.
- Fixed-size token chunking.
- Embedding generation for document chunks and queries.
- LanceDB-backed indexing for document embeddings.
- Retrieval of top-k nearest neighbors.
- Evaluation utilities for IR experiments.

## Known Limitations

- Only SciFact is wired up as the working example today.
- Chunking currently supports only the fixed token strategy.
- Embeddings are currently implemented with a single embedding backend.
- Vector search distance is hardcoded to `cosine`.
- `Indexer` currently mixes indexing and retrieval responsibilities.
- Table creation in `Indexer` has a convenience path that is useful for inserting embeddings, but it is not ideal for search-only usage.

## Planned Improvements

- Add support for the rest of the BEIR datasets.
- Add more chunking strategies.
- Add more embedding backends.
- Make LanceDB distance configuration selectable instead of hardcoded to `cosine`.
- Split indexing and retrieval into separate classes.
- Make search-only usage avoid any table creation or overwrite behavior.

## Notes

- If you want the fastest path to understand the system, start with [`notebooks/scifact_ir.ipynb`](./notebooks/scifact_ir.ipynb).
- The source code is intentionally small and easy to modify while the pipeline is still experimental.

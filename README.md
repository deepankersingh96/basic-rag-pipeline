# Basic RAG Pipeline

SciFact-first retrieval pipeline for experimenting with chunking, embeddings, LanceDB indexing, and evaluation on BEIR-style datasets.

The current end-to-end example lives in [`notebooks/scifact_ir.ipynb`](./notebooks/scifact_ir.ipynb).

## Overview

This project loads BEIR data, chunks documents, embeds chunks and queries, stores document embeddings in a vector database, retrieves the nearest matches for each query, and evaluates the results.

The pipeline is table-oriented inside LanceDB: each dataset can live in its own table, and the retriever selects the table by `dataset_name` at query time.

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

- Dataset selection by LanceDB table name.
- Document loading from BEIR-style JSONL files.
- Fixed-size token chunking.
- Embedding generation for document chunks and queries.
- LanceDB-backed indexing for document embeddings.
- Retrieval of top-k nearest neighbors from a named table.
- Configurable distance metrics for search.
- Evaluation utilities for IR experiments.

## Known Limitations

- Chunking currently supports only the fixed token strategy.
- Embeddings are currently implemented with a single embedding backend.
- Retrieval currently uses one search path for all datasets that share the same LanceDB schema.
- Search opens the requested table at query time instead of keeping a long-lived table handle per dataset.
- Table creation in `Indexer` is still oriented around indexing workflows, not search-only workflows.

## Planned Improvements

- Add more chunking strategies.
- Add more embedding backends.
- Add more retrieval-side options, such as per-dataset filtering or ranking tweaks.
- Add search-only helpers if the workflow starts needing them.
- Add LlamaIndex for chunking.

## Notes

- If you want the fastest path to understand the system, start with [`notebooks/scifact_ir.ipynb`](./notebooks/scifact_ir.ipynb).
- The source code is intentionally small and easy to modify while the pipeline is still experimental.

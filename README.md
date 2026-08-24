# Basic RAG Pipeline

BEIR-style dataset IR and RAG evaluation pipeline for experimenting with chunking, embeddings, LanceDB indexing, and retrieval metrics.

The current end-to-end example lives in [`notebooks/eval_beir_ir.ipynb`](./notebooks/eval_beir_ir.ipynb), and the pipeline now supports token, word, and sentence chunking strategies.

## Overview

This project loads BEIR data, chunks documents, embeds chunks and queries, stores document embeddings in a vector database, retrieves the nearest matches for each query, and evaluates the results.

The workflow is split cleanly between indexing and retrieval:

- The indexer prepares document chunks and writes them to LanceDB.
- The retriever opens the dataset table on demand and searches against the stored vectors.
- The evaluator collapses repeated chunk hits so each document only contributes its best score for a query.

The pipeline is table-oriented inside LanceDB: each dataset can live in its own table, and the retriever selects the table by `dataset_name` at query time.

## Quick Start

1. Download the BEIR datasets first:

   ```bash
   python datasets/beir/download.py
   ```

2. Open [`notebooks/eval_beir_ir.ipynb`](./notebooks/eval_beir_ir.ipynb).
3. Load the SciFact corpus and queries.
4. Choose a chunking strategy: token, word, or sentence.
5. Chunk the documents and generate embeddings for the resulting chunks.
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
│   ├── eval_beir_ir.ipynb
│   ├── ir_beir.ipynb
│   └── rag-cat-facts.ipynb
├── test/
│   ├── data/
│   │   └── architecture_of_tomorrow.md
│   └── test_chunking.py
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
- Multiple chunking strategies: token, word, and sentence.
- Embedding generation for document chunks and queries.
- LanceDB-backed indexing for document embeddings.
- Retrieval of top-k nearest neighbors from a named table.
- Configurable distance metrics for search.
- Evaluation utilities for IR experiments, including chunk-aware deduplication of repeated document hits.

## Known Limitations

- Embeddings are currently implemented with a single embedding backend.
- Retrieval currently uses one search path for all datasets that share the same LanceDB schema.
- Search opens the requested table at query time instead of keeping a long-lived table handle per dataset.

## Planned Improvements

- Add more embedding backends.
- Add more retrieval-side options, such as per-dataset filtering or **ranking** tweaks.
- Add search-only helpers if the workflow starts needing them.
- Add more chunking refinements as the corpus and evaluation needs evolve.
- ~~Add re-ranking to refine results.~~
- Separate Retriever and Re-ranker. 

## Notes

- If you want the fastest path to understand the system, start with [`notebooks/eval_beir_ir.ipynb`](./notebooks/eval_beir_ir.ipynb).
- The source code is intentionally small and easy to modify while the pipeline is still experimental.

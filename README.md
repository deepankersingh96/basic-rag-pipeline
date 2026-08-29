# Basic RAG Pipeline

Basic RAG Pipeline is a small BEIR-style IR and RAG evaluation project for experimenting with chunking, embeddings, LanceDB indexing, retrieval, and reranking.
It is built to make it easy to compare pipeline choices on a dataset-first workflow.

## Structure

```text
basic-rag-pipeline/
├── notebooks/
│   ├── eval_beir_ir.ipynb
│   └── rag-cat-facts.ipynb
├── src/basic_rag/
│   ├── chunking.py
│   ├── data.py
│   ├── embeddings.py
│   ├── evaluation.py
│   ├── index.py
│   ├── models.py
│   ├── reranking.py
│   └── retrieval.py
├── datasets/
│   └── beir/download.py
└── test/
    └── test_chunking.py
```

## How to Run

1. Install dependencies with `uv sync`.
2. Install the package in editable mode:

   ```bash
   uv pip install -e .
   ```

3. Download the BEIR datasets:

   ```bash
   uv run python datasets/beir/download.py
   ```

4. Open [`notebooks/eval_beir_ir.ipynb`](./notebooks/eval_beir_ir.ipynb).
5. Run the notebook end to end:
   - load data
   - chunk documents
   - embed chunks and queries
   - index into LanceDB
   - retrieve results
   - rerank results
   - evaluate the output

## Current Features

- BEIR-style dataset loading and evaluation.
- Token, word, and sentence chunking.
- Embedding, indexing, retrieval, and reranking components under `src/basic_rag/`.
- Notebook-driven end-to-end experimentation.

## Planned Improvements

- Add more embedding backends.
- Add more retrieval and reranking options.
- Expand evaluation helpers as the pipeline grows.

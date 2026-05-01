# SalesRAG

A conversational analytics system for querying Superstore sales data (2014–2017) using natural language. Built on a Retrieval-Augmented Generation (RAG) pipeline with ChromaDB, a CrossEncoder reranker and an LLM generator.

## Overview

SalesRAG lets you ask questions like:
- *"Which sub-categories have the lowest profit margins?"*
- *"How did the East region perform in 2016?"*
- *"What are the top selling products by revenue?"*

Instead of writing SQL or navigating dashboards, the system retrieves the relevant aggregated sales data and generates a natural language answer.

## Architecture

```
User Query
    │
    ▼
Table Router            (ranks collections based on relevancy)
    │
    ▼
Filter Adaptation       (keyword matching for metadata filter generation)
    │
    ▼
ChromaDB Retrieval      (vector search and filtering)
    │
    ▼
Reranker                (re-scores and trims candidate chunks)
    │
    ▼
LLM Generator           (produces final natural language answer)
```

## Project Structure

```
├── app/
│   ├── core/
│   │   ├── config/
│   │   │   ├── settings.py             # Configurations
│   │   │   └── logging.py              # Logger
│   │   ├── llm/
│   │   │   ├── llm.py                  # LLM generator
│   │   │   └── prompt.py               # Prompt builder
│   │   ├── rag/
│   │   │   ├── rerank.py               # Reranker
│   │   │   └── filter.py               # Per-collection filter generation
│   │   └── request.py                  # Handler — orchestrates the pipeline
│   ├── db/
│   │   └── engine.py
│   └── pipeline/
│       ├── process.py
│       └── load.py
├── interfaces/
│   └── cli/
│       ├── cli_main.py
│       └── spin.py
├── data/
│   ├── raw/
│   │   └── superstore.csv
│   └── processed/
├── tests/
│   └── test_pipeline/
├── main.py
├── README.md
└── requirements.txt
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

or

```bash
uv sync
```

### 2. Process and load

Running main.py builds the aggregation tables and populates ChromaDB:

```bash
python -m main.py
```

This will:
1. Parse the raw CSV and produce 14 aggregation tables
2. Generate natural language document summaries per row as JSONL files
3. Embed and load all documents into ChromaDB collections

In a case that errors occur with the database, passing a `--reload` flag to main.py forces a DB rebuild.

### 3. Run

After the database has been built the SalesRAG CLI will start and prompt for input. The CLI answers one question at a time until terminated.

## Collections

The system maintains 15 ChromaDB collections, each representing a different aggregation granularity:

| Collection | Description |
|---|---|
| `agg_month` | Monthly totals |
| `agg_quarter` | Quarterly totals |
| `agg_year` | Annual totals |
| `agg_item_category` | By product category |
| `agg_item_sub_category` | By product sub-category |
| `agg_city` | By city |
| `agg_state` | By state |
| `agg_region` | By region |
| `agg_product` | By individual product |
| `agg_month_x_category` | Month × category |
| `agg_year_x_category` | Year × category |
| `agg_state_x_category` | State × category |
| `agg_month_of_year` | Seasonal |
| `agg_region_x_year` | Region × year |
| `transactions` | Individual order records |

## Retrieval Strategy

The pipeline combines three different retrieval modes depending on the collection:

- **Routing**: collections are ranked by the CrossEncoder to reflect which tables most likely hold the target information.
- **Metadata sort**: fetches all rows and sorts by the metric implied by the query (sales, profit, margin, etc.).
- **Vector search**: HNSW semantic similarity search for all other collections.

## Tests

There are tests to query the RAG model with sample queries to check whether correct context is retrieved and the system works as expected. Running on CPU the full test suite will take some time.

```bash
pytest test_pipeline.py -v
```
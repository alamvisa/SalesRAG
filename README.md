# SalesRAG

```
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
│   │   └──superstore.csv
│   └── processed/
├── tests/
│   └── test_pipeline/
├── main.py
├── README.md
└── requirements.txt
```

## Setup

### 1. Install dependencies

pip install -r requirements.txt

or

uv sync

### 2. Process and load

Running main.py builds the aggregation tables and populates ChromaDB:

python -m main.py 

This will:
1. Parse the raw CSV and produce 14 aggregation tables
2. Generate natural language document summaries per row as JSONL files
3. Embed and load all documents into ChromaDB collections

In a case that errors occur with the database passing a `--reload` flag to main.py forces a DB rebuild.

### 4. Run

After the database has been built the SalesRAG CLI should start running and asks the user for an input.

The CLI will then proceed to answer one question a time and then ask for the next input until termination.

## Collections

The system maintains 15 ChromaDB collections, each representing a different aggregation granularity:

|         Collection      |    Description         |
|             ---         |        ---             |
|         `agg_month`     |    Monthly totals      |
|       `agg_quarter`     |     Quarterly totals   |
|         `agg_year`      |    Annual totals       |
|    `agg_item_category`  | By product category    |
| `agg_item_sub_category` | By product sub-category|
|       `agg_city`        |         By city        |
|        `agg_state`      |         By state       |
|       `agg_region`      |         By region      |
|       `agg_product`     | By individual product  |
| `agg_month_x_category`  |     Month × category   |
| `agg_year_x_category`   |     Year × category    |
| `agg_state_x_category`  |     State × category   |
| `agg_month_of_year`     |         Seasonal       |
| `agg_region_x_year`     |     Region × year      |
|   `transactions`        |Individual order records|

## Retrieval Strategy

The pipeline combines three different retrieval modes depending on the collection:

- **Metadata sort**: fetches all rows and sorts by the metadata implied by the query (sales, profit, margin, etc.).
- **Routing**: the aggregation tables are sorted in an order to reflect which tables most likely could hold the target information.
- **Vector search**: HNWS semantic similarity search for collections.

## Tests:

There are tests tp query the RAG model with sample queries to check wether correct context is retrieved and the system works on a basic level as expected. These queries do take some time and if running the models on CPU the entire test suite will take some time.

To run the RAG tests:

pytest test_pipeline.py -v

"""
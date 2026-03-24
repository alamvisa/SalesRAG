# SalesRAG

```
SalesRAG
├─ app
│  ├─ core
│  │  ├─ config
│  │  │  ├─ logging.py
│  │  │  └─ settings.py
│  │  ├─ llm
│  │  │  ├─ llm.py
│  │  │  └─ prompt.py
│  │  ├─ rag
│  │  │  ├─ filter.py
│  │  │  ├─ format.py
│  │  │  ├─ rerank.py
│  │  │  └─ retrieval.py
│  │  └─ request.py
│  ├─ db
│  │  ├─ engine.py
│  │  └─ schema.py
│  ├─ embedding
│  │  ├─ base.py
│  │  ├─ bert.py
│  │  └─ colbert.py
│  ├─ ingest.py
│  └─ pipeline
│     ├─ chunking.py
│     ├─ index.py
│     ├─ load.py
│     └─ process.py
├─ data
│  ├─ processed
│  └─ raw
│     └─ superstore.csv
├─ interfaces
│  └─ cli
│     ├─ cli_main.py
│     └─ spin.py
├─ main.py
├─ README.md
├─ requirements.txt
└─ tests

```
import json
from pathlib import Path
from app.core.config.settings import config
import pandas as pd
from app.db.engine import EmbeddingFunction, get_client

def get_ef():
    return EmbeddingFunction()
    

def load_collection(collection_name: str, table_name: str, client):
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    path = config.DATA_PROCESSED_DIR / "documents" / f"{table_name}_document.jsonl"
    documents, metadatas, ids = [], [], []
    
    with open(path) as f:
        for i, line in enumerate(f):
            record = json.loads(line)
            documents.append(record["text"])
            metadatas.append(record["metadata"])
            ids.append(f"{table_name}_{i}")
    
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return collection

def load_csv(collection):
    path = config.DATA_PROCESSED_DIR / "processed_superstore.csv"
    documents, metadatas, ids = [], [], []
    df = pd.read_csv(path)
    for i, row in df.iterrows():
        documents.append(row["description"])
        metadatas.append({
            "type": "transaction",
            "year": int(row["Order Date"][:4]),
            "month": int(row["Order Date"][5:7]),
            "category": row["Category"],
            "sub-category": row["Sub-Category"],
            "region": row["Region"],
            "state": row["State"],
            "city": row["City"],
            "product": row["Product Name"],
            "sales": row["Sales"],
            "profits": row["Profit"],
            "margin": round(row["Profit"] / row["Sales"], 4) if row["Sales"] else 0,
            "discount": row["Discount"]
        })
        ids.append(f"transaction_{i}")
    
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

def build_all_collections(aggregate_tables, client):
    collections = {}
    for table_name in aggregate_tables:
        collections[table_name] = load_collection(table_name, table_name, client)
    return collections

def load():
    client = get_client()
    aggregate_tables = [
        'agg_month',
        'agg_quarter',
        'agg_year',
        'agg_item_category',
        'agg_item_sub_category',
        'agg_city',
        'agg_state',
        'agg_region',
        'agg_product',
        'agg_month_x_category',
        'agg_year_x_category',
        'agg_state_x_category',
        'agg_month_of_year',
        'agg_region_x_year'
    ]
    collections = build_all_collections(aggregate_tables, client)
    transactions = client.get_or_create_collection(
        name="transactions",
        metadata={"hnsw:space": "cosine"}
    )
    load_csv(transactions)
    collections["transactions"] = transactions
    return collections
import json
from pathlib import Path
from app.core.config.settings import config
import pandas as pd
from app.db.engine import get_client, reset_client, return_ef
import shutil

def get_ef():
    return return_ef()
    

def load_collection(collection_name: str, table_name: str, client, ef):
    """
    Loads a JSONL document file into a ChromaDB collection, using cosine similarity.
    """
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
        
    )
    path = config.DATA_PROCESSED_DIR / "documents" / f"{table_name}_document.jsonl"
    documents, metadatas, ids = [], [], []
    with open(path) as f:
        for i, line in enumerate(f):
            record = json.loads(line)
            documents.append(record["text"])
            metadatas.append(record["metadata"])
            ids.append(f"{table_name}_{i}")

    batch_size = 5000
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
    return collection

def load_csv(collection):
    """
    Loads the processed transactions CSV into the transactions collection.
    """
    path = config.DATA_PROCESSED_DIR / "processed_superstore.csv"
    documents, metadatas, ids = [], [], []
    df = pd.read_csv(path)
    for i, row in df.iterrows():
        documents.append(row["description"])
        metadatas.append({
            "type": "transaction",
            "year": int(row["Order Date"][:4]),
            "month": int(row["Order Date"][5:7]),
            "category": str(row["Category"]),
            "sub-category": str(row["Sub-Category"]),
            "region": str(row["Region"]),
            "state": str(row["State"]),
            "city": str(row["City"]),
            "product": str(row["Product Name"]),
            "sales": float(row["Sales"]),
            "profits": float(row["Profit"]),
            "margin": round(float(row["Profit"]) / float(row["Sales"]), 4) if row["Sales"] else 0.0,
            "discount": float(row["Discount"])
        })
        ids.append(f"transaction_{i}")

    batch_size = 5000
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )

def build_all_collections(aggregate_tables, client, ef):
    """
    Loads each aggregation table's JSONL into its own ChromaDB collection.
    """
    collections = {}
    for table_name in aggregate_tables:
        collections[table_name] = load_collection(table_name, table_name, client, ef)
    return collections

def load():
    chroma_path = config.DATA_PROCESSED_DIR / config.DB_NAME
    reset_client()
    if chroma_path.exists():
        print("Clearing existing ChromaDB...")
        shutil.rmtree(chroma_path)
    client = get_client()
    ef = get_ef()
    aggregate_tables = [
        'agg_month', 'agg_quarter', 'agg_year',
        'agg_item_category', 'agg_item_sub_category',
        'agg_city', 'agg_state', 'agg_region', 'agg_product',
        'agg_month_x_category', 'agg_year_x_category',
        'agg_state_x_category', 'agg_month_of_year', 'agg_region_x_year'
    ]
    collections = build_all_collections(aggregate_tables, client, ef)
    transactions = client.get_or_create_collection(
        name="transactions",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
        
    )
    load_csv(transactions)
    collections["transactions"] = transactions
    return collections

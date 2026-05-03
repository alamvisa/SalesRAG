from sentence_transformers import SentenceTransformer
from chromadb import Documents, EmbeddingFunction, Embeddings
import chromadb
from app.core.config.settings import config
import torch

collection_names = {
    'agg_month': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "month", "year"],
    'agg_quarter': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "quarter", "year"], 
    'agg_year': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "year"],
    'agg_item_category': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "category"], 
    'agg_item_sub_category': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "sub-category"],
    'agg_city': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "city"], 
    'agg_state': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "state"], 
    'agg_region': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "region"], 
    'agg_product': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "product"],
    'agg_month_x_category': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "month", "year", "category"], 
    'agg_year_x_category': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "year", "category"],
    'agg_state_x_category': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "state", "category"], 
    'agg_month_of_year': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "month"],
    'agg_region_x_year': ["type", "sales", "profits", "quantity", "margin", "discount_rate", "region", "year"], 
    'transactions': ["type"]
}

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(config.DATA_PROCESSED_DIR / config.DB_NAME))
    return _client

def reset_client():
    """
    Clear the singleton so the next get_client() opens a fresh connection.
    """
    global _client
    _client = None

class EmbeddingF(EmbeddingFunction):
    """
    Wraps a SentenceTransformer to produce normalised embeddings for ChromaDB.
    """
    def __init__(self, model_name=config.EMBEDDING_MODEL):
        self.device = "cpu"
        self.model = SentenceTransformer(model_name, device = self.device)
        
    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input, normalize_embeddings=True, show_progress_bar=False).tolist()
    
def get_collections(selected_tables = collection_names.keys()):
    """
    Return a fresh dict of ChromaDB Collection objects for the given table names.
    """
    client = get_client()
    
    return {
        name: client.get_collection(name=name, embedding_function=ef)
        for name in selected_tables
    }

def query(collections, query_text, filters = None):
    """
    Query each collection by vector similarity and return all hits below the
    distance threshold, sorted nearest-first.
    Filters are stripped to only the fields present in each collection's schema.
    """
    results = []
    for name, collection in collections.items():

        n = min(config.N_RESULTS, collection.count())
        if name == "" or collection.count() == 0:
            continue
        query_kwargs = dict(
            query_texts=[query_text],
            n_results=n,
            include=["documents", "metadatas", "distances"]
        )
        if filters:
            active_filters = {}
            for key, value in filters.items():
                if key in collection_names[name]:
                    active_filters[key] = value
            if active_filters:
                query_kwargs["where"] = active_filters
        try:
            hits = collection.query(**query_kwargs)
        except Exception as e:
            print(e)
            print(f"At collection {name}")

        for doc, meta, dist in zip(
            hits["documents"][0],
            hits["metadatas"][0],
            hits["distances"][0]
        ):
            if dist >= config.THRESHOLD:
                continue

            results.append({
                "text": doc,
                "metadata": meta,
                "distance": dist,
                "source": name
            })

    return sorted(results, key=lambda x: x["distance"])

def return_ef():
    return ef

ef = EmbeddingF()
_client = None
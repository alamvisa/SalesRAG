from sentence_transformers import SentenceTransformer
from chromadb import Documents, EmbeddingFunction, Embeddings
import chromadb
from app.core.config.settings import config
import torch

collection_names = [
    'agg_month', 'agg_quarter', 'agg_year',
    'agg_item_category', 'agg_item_sub_category',
    'agg_city', 'agg_state', 'agg_region', 'agg_product',
    'agg_month_x_category', 'agg_year_x_category',
    'agg_state_x_category', 'agg_month_of_year',
    'agg_region_x_year', 'transactions'
]

_client = None

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(config.DATA_PROCESSED_DIR / config.DB_NAME))
    return _client

def reset_client():
    global _client
    _client = None

class EmbeddingF(EmbeddingFunction):
    def __init__(self, model_name=config.EMBEDDING_MODEL):
        #self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = "cpu"
        self.model = SentenceTransformer(model_name, device = self.device)
        
    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input, normalize_embeddings=True).tolist()
    
def get_collections():
    client = get_client()
    ef = EmbeddingF()

    return {
        name: client.get_collection(name=name, embedding_function=ef)
        for name in collection_names
    }

def query(collections, query_text, filters = None):
    results = []
    for name, collection in collections.items():

        n = min(config.N_RESULTS, collection.count())
        print(f"Querying {name}, count={n}")
        if name == "":
            pass
        query_kwargs = dict(
            query_texts=[query_text],
            n_results=n,
            include=["documents", "metadatas", "distances"]
        )
        if filters:
            query_kwargs["where"] = filters
        hits = collection.query(**query_kwargs)

        for doc, meta, dist in zip(
            hits["documents"][0],
            hits["metadatas"][0],
            hits["distances"][0]
        ):
            if dist < config.THRESHOLD:
                results.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": dist,
                    "source": name
                })

    return sorted(results, key=lambda x: x["distance"])

# def check_db():
#     chroma_path = config.DATA_PROCESSED_DIR / config.DB_NAME
#     if not chroma_path.exists():
#         return False
#     try:
#         client = get_client()
#         existing = {c.name for c in client.list_collections()}
#         if not all(name in existing for name in collection_names):
#             return False
#         for name in collection_names:
#             col = client.get_collection(name)
#             if col.count() == 0:
#                 return False
#         return True
#     except Exception:
#         reset_client()
#         return False
from sentence_transformers import SentenceTransformer
from chromadb import Documents, EmbeddingFunction, Embeddings
import chromadb
from app.core.config.settings import config

def get_client():
    return chromadb.PersistentClient(path=str(config.DATA_PROCESSED_DIR / config.DB_NAME))

class EmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name=config.EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        
    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input, normalize_embeddings=True).tolist()
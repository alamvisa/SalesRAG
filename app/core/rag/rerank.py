from sentence_transformers import CrossEncoder
from app.core.config.logging import logger
import json

class ranker():
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L6-v2')

    def rank(self, query, chunks):
        logger.info(json.dumps({
            "retrieved context": {"chunks": chunks}
        }))

        q = [(query, c["text"]) for c in chunks]
        scores = self.model.predict(q)
        ranked = zip(chunks, scores)
        ranked = sorted(ranked, key=lambda x: x[1], reverse=True)
        top = [c for c, _ in ranked[:5]]
        return top
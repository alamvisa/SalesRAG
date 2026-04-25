from sentence_transformers import CrossEncoder
from app.core.config.logging import logger
import json

class ranker():
    def __init__(self):
        model = 'cross-encoder/ms-marco-electra-base'
        self.model = CrossEncoder(model)
        logger.info(f"Load pretrained reranker model: {model}")

    def rank(self, query, chunks):
        logger.info(json.dumps({
            "retrieved context": {"chunks": chunks}
        }))

        q = [(query, c["text"]) for c in chunks]
        scores = self.model.predict(q)
        ranked = zip(chunks, scores)
        ranked = sorted(ranked, key=lambda x: x[1], reverse=True)
        top = [c for c, s in ranked if s >= ranked[0][1]*0.2][:12]
        logger.info(json.dumps({
            "reranked context": {"Chunks returned": len(top), "chunks": [{"text": c["text"], "score": round(float(s), 4)} for c, s in ranked[:7]]}
        }))
        return top
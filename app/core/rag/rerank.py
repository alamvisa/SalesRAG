from sentence_transformers import CrossEncoder
from app.core.config.logging import logger
from app.core.config.settings import config
import json

class ranker():
    def __init__(self):
        model = 'cross-encoder/ms-marco-electra-base'
        self.model = CrossEncoder(model)
        logger.info(f"Load pretrained reranker model: {model}")
        self.table_desc = {
            "agg_month":             "Monthly aggregated sales totals",
            "agg_quarter":           "Quarterly aggregated sales, Q1–Q4 trends",
            "agg_year":              "Annual aggregated sales, year-over-year comparisons",
            "agg_item_category":     "Sales broken down by product category",
            "agg_item_sub_category": "Sales broken down by product sub-category",
            "agg_city":              "Sales performance by city",
            "agg_state":             "Sales performance by state",
            "agg_region":            "Overall sales performance by region (East, West, Central, South)",
            "agg_product":           "Sales data for individual products",
            "agg_month_x_category":  "Monthly sales broken down by product category, monthly data",
            "agg_year_x_category":   "Annual sales broken down by product category, yearly data",
            "agg_state_x_category":  "State-level sales broken down by product category",
            "agg_month_of_year":     "Seasonal patterns. How each calendar month performs across all years",
            "agg_region_x_year":     "Regional sales broken down by year, region trends over time",
            "transactions":          "Individual order-level transaction records",
        }

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
    
    def route(self, query: str) -> list[str]:
        tables = list(self.table_desc.keys())
        pairs = [(query, self.table_desc[t]) for t in tables]
        scores = self.model.predict(pairs)

        scored = sorted(zip(tables, scores), key=lambda x: x[1], reverse=True)
        best = scored[0][1]
        selected = [t for t, s in scored if s + 0.01 >= best * config.ROUTER_THRESHOLD]

        logger.info({
            "table_routing": {
                "query": query,
                "selected": selected,
                "scores": {t: round(float(s), 4) for t, s in scored}
            }
        })
        return selected
        
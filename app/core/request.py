import time
from app.db.engine import get_collections, query, reset_client
from app.core.llm.llm import generator
from app.core.llm.prompt import get_prompt
from app.core.rag.rerank import ranker
from app.core.rag.filters import get_filters
from app.core.config.logging import logger
import json


class Handler():
    """
    Orchestrates the full RAG pipeline
    """
    def __init__(self, disable_generator = False):
        self.input = None
        self.context = None
        self.generator = None
        if not disable_generator:
            self.generator = generator()
        self.ranker = ranker()

    def new_input(self, input):
        logger.info(json.dumps({
            "New user query": {"query": input}
        }))
        self.input = input

    def retrieve(self):
        """
        Route the query to relevant collections, apply filters, retrieve and rerank chunks.
        """
        selected_tables = self.ranker.route(self.input)
        collection = get_collections(selected_tables)
        filters = get_filters(self.input)
        retrieved = query(collection, self.input, filters=filters)
        self.context = self.ranker.rank(self.input, retrieved)

    def generate(self):
        """
        Format reranked context into a prompt and return the LLM response.
        """
        if self.generator is None:
            return
        context = get_prompt(self.context)
        return self.generator.gen(self.input, context)
    
    def get_context(self):
        return self.context
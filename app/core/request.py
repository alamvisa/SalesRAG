import time
from app.db.engine import get_collections, query
from app.core.llm.llm import generator
from app.core.llm.prompt import get_prompt
from app.core.rag.rerank import ranker
#from app.core.rag.filter import filt
from app.core.config.logging import logger
import json


class Handler():
    def __init__(self, disable_generator = False):
        #self.collection = get_collections()
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
        collection = get_collections()
        retrieved = query(collection, self.input)#, self.filters)
        self.context = self.ranker.rank(self.input, retrieved)

    def generate(self):
        if self.generator is None:
            return
        context = get_prompt(self.context)
        return self.generator.gen(self.input, context)
    
    def get_context(self):
        return self.context
    
# h = Handler(disable_generator=True)
# inp = "What is the sales trend over the 4-year period?"
# h.new_input(inp)
# h.filter()
# h.retrieve()
# print([c for c in h.get_context() if c["source"] == "agg_year"])
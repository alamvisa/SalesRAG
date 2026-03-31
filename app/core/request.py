import time
from app.db.engine import get_collections, query
from app.core.llm.llm import generator
from app.core.llm.prompt import get_prompt
from app.core.rag.format import form
from app.core.rag.rerank import ranker
from app.core.rag.filter import filt
from app.core.config.logging import logger
import json


class Handler():
    def __init__(self, disable_generator = False):
        self.collection = get_collections()
        self.input = None
        self.context = None
        self.filters = None
        self.generator = None
        if not disable_generator:
            self.generator = generator()
        self.ranker = ranker()

    def new_input(self, input):
        logger.info(json.dumps({
            "New user query": {"query": input}
        }))
        self.input = input

    def process(self):
        self.input = form(self.input)

    def filter(self):
        self.filters = filt(self.input)

    def retrieve(self):
        retrieved = query(self.collection, self.input, self.filters)
        self.context = self.ranker.rank(self.input, retrieved)

    def generate(self):
        if self.generator == None:
            return
        system_prompt, context = get_prompt(self.input, self.context)
        return self.generator.gen(self.input, system_prompt, context)
    
    def get_context(self):
        return self.context
    
# h = Handler(disable_generator=True)
# inp = "How are the sales doing in Philadelphia?"
# h.new_input(inp)
# h.process()
# h.filter()
# h.retrieve()
# print([c for c in h.get_context() if c["metadata"]["type"] == "city"])
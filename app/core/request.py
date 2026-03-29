import time
from app.db.engine import get_collections, query
from app.core.llm.llm import generator
from app.core.llm.prompt import get_prompt
from app.core.rag.format import form
from app.core.rag.rerank import rank
from app.core.rag.filter import filt


class Handler():
    def __init__(self):
        self.collection = get_collections()
        self.input = None
        self.context = None
        self.filters = None
        self.generator = generator()

    def new_input(self, input):
        self.input = input

    def process(self):
        self.input = form(self.input)

    def filter(self):
        self.filters = filt(self.input)

    def retrieve(self):
        retrieved = query(self.collection, self.input, self.filters)
        self.context = rank(retrieved)

    def generate(self):
        system_prompt, context = get_prompt(self.input, self.context)
        return self.generator.gen(self.input, system_prompt, context)
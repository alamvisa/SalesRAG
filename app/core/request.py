import time

class Handler():
    def __init__(self):
        self.input = None

    def new_input(self, input):
        self.input = input

    def process(self):
        time.sleep(2)
        return 1

    def filter(self):
        time.sleep(1)
        pass

    def retrieve(self):
        time.sleep(1)
        pass

    def generate(self):
        time.sleep(3)
        return "kappachungus"
from app.core.request import Handler
from interfaces.cli.spin import Spinner
from app.pipeline.load import load

def run(l):
    spinner = Spinner()
    print("========= SalesRAG =========")
    try:
        if l:
            #spinner.start("Generating embedding...")
            load()
            print("Done!")
            #spinner.stop()
        handler = Handler()
        while True:
            
            context = input("Input: ")
            spinner.start("Processing query...")
            handler.new_input(context)
            response = handler.process()

            if response == 1:
                spinner.update("Filtering...")
                handler.filter()

            spinner.update("Retrieving...")
            handler.retrieve()

            spinner.update("Generating response...")
            response = handler.generate()
            print(f"\nSalesBot: {response}")
            spinner.stop()

        print("Exiting...")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    

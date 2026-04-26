from app.core.request import Handler
from interfaces.cli.spin import Spinner
from app.pipeline.load import load

def run(load_required):
    spinner = Spinner()
    print("========= SalesRAG =========")
    try:
        if load_required:
            load()
            print("Done!")
        handler = Handler()
        while True:
            try:
                context = input("Input: ")
                spinner.start("Processing query...")
                handler.new_input(context)

                # response = handler.process()
                # if response == 1:
                #     spinner.update("Filtering...")
                #     handler.filter()

                spinner.update("Retrieving...")
                handler.retrieve()

                spinner.update("Generating response...")
                response = handler.generate()
                print(f"\nSalesBot: {response}")
                spinner.stop()
            except Exception as e:
                print(f"\nError: {e}")
            finally:
                spinner.stop()

    
    except KeyboardInterrupt:
        print("\nExiting...")
    

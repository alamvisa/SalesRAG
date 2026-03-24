from app.core.request import Handler
from interfaces.cli.spin import Spinner

def run():
    spinner = Spinner()
    handler = Handler()
    print("========= SalesRAG =========")
    try:
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
            break

        print("Exiting...")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    

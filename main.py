import os
import sys
import warnings
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"   
from interfaces.cli.cli_main import run
from app.pipeline.process import process
from app.core.config.settings import config
warnings.filterwarnings("ignore")

def re_process():
    processed = os.listdir("data/processed/documents/")
    for file_r in processed:
        os.unlink("data/processed/documents/" + file_r)
    raw = os.listdir("data/raw")
    for file_r in raw:
        process(file_r)
    

if __name__ == "__main__":
    load = False
    if (len(sys.argv) > 1 and sys.argv[1] == "--reload") or not os.path.exists(f"data/processed/{config.DB_NAME}"):
        load = True
        print("Reloading DB...")
        re_process()

    run(load)
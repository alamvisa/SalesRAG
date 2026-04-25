import os
import logging
import warnings

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
#os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
#os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(__import__('pathlib').Path.home() / ".cache" / "sentence_transformers")

warnings.filterwarnings("ignore")

from interfaces.cli.cli_main import run
from app.pipeline.process import process
from app.core.config.settings import config
import sys
import os

def check():
    chroma_path = config.DATA_PROCESSED_DIR / "chroma"
    if chroma_path.exists():
        return False
    return True
        
def re_process():
    processed = os.listdir("data/processed/documents/")
    for file_r in processed:
        os.unlink("data/processed/documents/" + file_r)
    raw = os.listdir("data/raw")
    for file_r in raw:
        process(file_r)
    

if __name__ == "__main__":
    load = check()
    if len(sys.argv) > 1 and sys.argv[1] == "--reload":
        load = True
        print("Reloading DB...")
        re_process()

    
    run(load)
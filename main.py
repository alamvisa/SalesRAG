import os
import logging
import warnings

# os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
# os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
# os.environ["TOKENIZERS_PARALLELISM"] = "false"
# os.environ["HF_HUB_VERBOSITY"] = "error"
# os.environ["TRANSFORMERS_VERBOSITY"] = "error"
# os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(__import__('pathlib').Path.home() / ".cache" / "sentence_transformers")

# warnings.filterwarnings("ignore")

from interfaces.cli.cli_main import run
from app.pipeline.process import process
import pathlib
import os
from app.core.config.settings import config

def check():
    chroma_path = config.DATA_PROCESSED_DIR / "chroma"
    if chroma_path.exists():
        return False
    processed = os.listdir("data/processed")
    raw = os.listdir("data/raw")
    for file_r in raw:
        if f"p_{file_r}" not in processed:
            process(file_r)
    return True
        


if __name__ == "__main__":
    load = check()
    run(load)
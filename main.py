from interfaces.cli.cli_main import run
from app.pipeline.process import process
import pathlib
import os

def check():
    processed = os.listdir("data/processed")
    raw = os.listdir("data/raw")
    for file_r in raw:
        if f"p_{file_r}" not in processed:
            process(file_r)


if __name__ == "__main__":
    check()
    #run()
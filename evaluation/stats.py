from os import environ, listdir
from logging import info, warning, debug, basicConfig

from fire import Fire
from tqdm import tqdm

from  parse_logs import parse

def calculate_perfect_validation(log, corpus, run):
    max_valid = (0,0)
    max_train = (0,0)
    for step, entry in enumerate(log[corpus]["train"][run]["steps"]):
        max_valid = (entry.get("step",0), entry.get("valid_accuracy",0)) if entry.get("valid_accuracy",0) > max_valid[1] else max_valid
        max_train = (entry.get("step",0), entry.get("valid_accuracy",0)) if entry.get("valid_accuracy",0) > max_valid[1] else max_valid
    return {"valid": max_valid, "train": max_train}

if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
    Fire({"parse": parse})

from os import environ, listdir
from logging import info, warning, debug, basicConfig

from fire import Fire
from tqdm import tqdm

from  parse_logs import parse

def calculate_perfect_validation(log, corpus, run):
    max_valid = (0, 0)
    max_train = (0, 0)
    for step, entry in enumerate(log[corpus]["train"][run]["steps"]):
        max_valid = (
                    float(entry.get("step", 0)),
                    float(entry.get("valid_accuracy", 0))
                ) if float(entry.get("valid_accuracy", 0)) > max_valid[1] else max_valid
        max_train = (
                    float(entry.get("step", 0)),
                    float(entry.get("train_accuracy", 0))
                ) if float(entry.get("train_accuracy", 0)) > max_train[1] else max_train
    return {"valid": max_valid, "train": max_train}

def sizeof_fmt(num, suffix='B'):
    """
    formats bytes in a human readable way.
    https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
    Fire({"parse": parse})

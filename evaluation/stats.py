from os import environ, listdir
from logging import info, warning, debug, basicConfig

from fire import Fire
from tqdm import tqdm

from  parse_logs import parse

def calculate_perfect_validation(log, corpus, run):
    max_valid = {"accuracy": 0}
    max_train = {"accuracy": 0}
    for step, entry in enumerate(log[corpus]["train"][run]["steps"]):
        max_valid = {
                        "step": entry.get("step", 0),
                        "accuracy": float(entry.get("valid_accuracy", 0))
                    } if float(entry.get("valid_accuracy", 0)) > max_valid["accuracy"] else max_valid
        max_train = {
                        "step": entry.get("step", 0),
                        "accuracy": float(entry.get("train_accuracy", 0))
                } if float(entry.get("train_accuracy", 0)) > max_train["accuracy"] else max_train
    best_score = {"valid": max_valid, "train": max_train}

    if not log[corpus]["train"][run]["scores"]:
        return best_score

    for run in log[corpus]["train"][run]["scores"]:
        if run["score_type"] not in best_score:
            best_score[run["score_type"]] = {}

        for score, value in run.items():
            if score in ["run_dir", "model", "score_type", "step"]:
                continue
            best_score[run["score_type"]][score] = {
                    "step": run["step"],
                    score: float(value)
                    } if float(value) > best_score[run["score_type"]].get(score, {score: -1.0})[score] else best_score[run["score_type"]][score]
    return best_score


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

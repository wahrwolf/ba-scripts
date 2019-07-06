from itertools import product
from os import environ
from logging import info, warning, debug, basicConfig
from tqdm import tqdm
from parse_logs import parse
from stats import calculate_perfect_validation


# list of HYPERPARAMS
HYPERPARAMS = {
        "optim": ["sgd", "adadelta", "adam"],
        "learning_rate": [1.0, 0.1, 0.01, 0.001],
        "start_decay_steps": [None, 19750, 9875]
    }

LOG_FILES = ["/srv/ftp/share/archive/training/Clean-cs-en/logs", "/srv/ftp/share/archive/training/Clean-de-en/logs", "/srv/ftp/share/archive/training/Tagged-cs-en/logs", "/srv/ftp/share/archive/training/Tagged-de-en/logs"]

HYPER_CONFIGS = [i for i in product(HYPERPARAMS["optim"], HYPERPARAMS["learning_rate"], HYPERPARAMS["start_decay_steps"])]

def build_result_table(schedule, trainings_reports):
    # build table with possible configs
    result_table = {}

    for corpus in trainings_reports.keys():
        debug(f"Corpus: {corpus} with {len(trainings_reports[corpus]['train'])}")
        result_table[corpus] = {}
        for config in schedule:
            for run in trainings_reports[corpus]["train"]:
                params = run["params"]
                current_config = (
                    params.get("optim", "sgd"),
                    params.get("learning_rate", 1),
                    params.get("start_decay_steps", None)
                )
                debug(f"{current_config}")
                if config == current_config:
                    debug(f"Found model in {params.get('path')} for {config}")
                    if config not in result_table[corpus]:
                        result_table[corpus][config] = []
                    result_table[corpus][config].append(params["path"])
            if config not in result_table[corpus]:
                debug(f"No model found for {config}")
            elif len(result_table[corpus][config]) < 3:
                debug(f"Only {len(result_table[corpus][config])} models found for {config}! Needed 3")
    return result_table

def load_scores(reports):
    result_table = {}
    for corpus in reports.keys():
        result_table[corpus] = {}
        debug(f"Loading scores for {corpus}")
        for config, models in reports[corpus].items():
            result_table[corpus][config] = {}
            for run, model in enumerate(models):
                log_file = parse(model)
                scores = calculate_perfect_validation(log_file, corpus, 0)
                result_table[corpus][config] = {model: scores}
    return result_table


if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])

    # get list of logs
    logs = parse(LOG_FILES)
    results = build_result_table(HYPER_CONFIGS, logs)
    load_scores(results)

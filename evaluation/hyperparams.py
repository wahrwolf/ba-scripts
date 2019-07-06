from itertools import product
from prettytable import PrettyTable
from os import environ
from logging import info, warning, debug, basicConfig
from tqdm import tqdm
from parse_logs import parse
from stats import calculate_perfect_validation


# list of HYPERPARAMS
HYPERPARAMS = {
        "optim": ["sgd", "adadelta", "adam"],
        "learning_rate": ['1', '0.1', '0.01', '0.001'],
        "start_decay_steps": [None, '19750', '9875']
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

def load_scores(result_table):
    for corpus in result_table.keys():
        for config, models in result_table[corpus].items():
            for run, model in enumerate(models):
                log_file = parse(model)
                scores = calculate_perfect_validation(log_file, corpus, 0)
                models[run] = scores
            result_table[corpus][config] = sorted(models, key=lambda models: models["valid"][1])[::-1]
    return result_table


if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])

    # get list of logs
    logs = parse(LOG_FILES)
    results = build_result_table(HYPER_CONFIGS, logs)
    clean_scores = load_scores(results)

    for corpus in clean_scores.keys():
        print(f"{corpus}:")
        print("Valid trainings runs:")
        print("---------------------")
        for config, models in clean_scores[corpus].items():
            if not models[0]["valid"] == (0, 0):
                print(f"\t{config}; valid:{models[0]['valid']}; train:{models[0]['train']}")
        print("Missing trainings runs:")
        print("-----------------------")
        for config in HYPER_CONFIGS:
            if config not in clean_scores[corpus]:
                print(f"\t3x {config}")
            else:
                clean_runs = [m for m in clean_scores[corpus][config] if m["valid"] == (0, 0)]
                if len(clean_runs) < 3:
                    print(f"\t{3 - len(clean_runs)}x {config}")

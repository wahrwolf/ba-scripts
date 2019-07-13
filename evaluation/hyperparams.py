from itertools import product
from sys import argv
from os import environ
from logging import info, warning, debug, basicConfig
from parse_logs import parse
from stats import calculate_perfect_validation


# list of HYPER_PARAMS
HYPER_PARAMS = {
        "Clean-de-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": [None, '9875', '19750']
        }, "Tagged-de-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": [None, '9875', '19750']
        }, "Clean-cs-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": [None, '21500', '10750']
        }, "Tagged-cs-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": [None, '21500', '10750']
        }
    }

LOG_FILES = {
        "Clean-de-en" : [
            "/srv/ftp/share/archive/training/Clean-de-en/logs",
            "/srv/ftp/share/archive/wtmgws2/data/Clean-de-en/logs",
            "/srv/ftp/share/archive/wtmgws3/data/Clean-de-en/logs",
            "/srv/ftp/share/archive/wtmgws4/data/Clean-de-en/logs",
            "/srv/ftp/share/archive/wtmgws6/data/Clean-de-en/logs"
        ], "Tagged-de-en" : [
            "/srv/ftp/share/archive/training/Tagged-de-en/logs",
            "/srv/ftp/share/archive/wtmgws2/data/Tagged-de-en/logs",
            "/srv/ftp/share/archive/wtmgws3/data/Tagged-de-en/logs",
            "/srv/ftp/share/archive/wtmgws4/data/Tagged-de-en/logs",
            "/srv/ftp/share/archive/wtmgws6/data/Tagged-de-en/logs"
        ], "Clean-cs-en" : [
            "/srv/ftp/share/archive/training/Clean-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws2/data/Clean-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws3/data/Clean-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws4/data/Clean-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws6/data/Clean-cs-en/logs"
        ], "Tagged-cs-en" : [
            "/srv/ftp/share/archive/training/Tagged-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws2/data/Tagged-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws3/data/Tagged-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws4/data/Tagged-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws6/data/Tagged-cs-en/logs"
        ]
    }

HYPER_CONFIGS = {
        corpus: list(dict(zip(params.keys(), value))
                    for value in product(*params.values())
            )
            for corpus, params in HYPER_PARAMS.items()
        }

def build_result_table(schedule, trainings_reports):
    # build table with possible configs
    result_table = {}
    for corpus in schedule:
        if corpus not in trainings_reports:
            warning(f"No entries for corpus {corpus} in reports found! Skipping...")
            continue
        debug(f"Corpus: {corpus} with {len(trainings_reports[corpus]['train'])} runs")
        result_table[corpus] = []
        for config in schedule[corpus]:
            for run in trainings_reports[corpus]["train"]:
                params = run["params"]
                current_config = {k: v for k, v in params.items() if k in config}

                if config == current_config:
                    debug(f"Found model in {params.get('path')} for {config}")
                    result_table[corpus].append(dict(config,**{"path": params["path"]}))
            if config not in result_table[corpus]:
                debug(f"No model found for {config}")
            elif len([run for run in result_table[corpus] if run == config]) < 3:
                debug(f"Not enough models found for {config}! Needed 3")
    return result_table

def load_scores(result_table):
    for corpus in result_table:
        for run in result_table[corpus]:
            log_file = parse(run["path"])
            scores = calculate_perfect_validation(log_file, corpus, 0)
            run["scores"] = scores
            #sort the entries by validation score in reverese order
        result_table[corpus] = sorted(result_table[corpus], key=lambda run: run["scores"]["valid"][1])[::-1]
    return result_table

def build_trainings_config(schedule, trainings_scores):
    missing_configs = {}
    for corpus in schedule:
        if corpus not in trainings_scores:
            warning(f"No entries for corpus {corpus} in reports found! Skipping...")
            continue
        missing_configs[corpus] = [
                                    config for config in HYPER_CONFIGS[corpus]
                                        if config not in trainings_scores[corpus]
                                        or trainings_scores[corpus][config][0]["valid"] == (0, 0)
                                  ]
    return missing_configs

def main(argv):
    corpora = [corpus for corpus in argv[1:] if corpus in LOG_FILES]

    # get list of logs
    logs = parse(
                # Load only files from current selection
                [log for corpus, files in LOG_FILES.items() for log in files if corpus in corpora]
            )
    results = build_result_table(
                {corpus: configs for corpus, configs in HYPER_CONFIGS.items() if corpus in corpora},
                logs
            )
    clean_scores = load_scores(results)

    for corpus in corpora:
        print(f"{corpus}:")
        print("Valid trainings runs:")
        print("---------------------")
        for run in clean_scores[corpus]:
            if not run["scores"]["valid"] == (0, 0):
                print({k: v for k, v in run.items() if k != "path"})
## <READ THIS> ##
# hello future wolf
# you have to fix the comparison of dicts in the next paragraph
# currently it will try to compare the scheduled run (config) with the acutal runs.
# the actual runs contain more keys and therefore the comaprison will always fail
# you have to either find a way to only compare a part of the dicts (e.g. by reducing the dicts)
# or go through everything! Good luck!
#        print("Missing trainings runs:")
#        print("-----------------------")
#        for config in HYPER_CONFIGS[corpus]:
#            if config not in clean_scores[corpus]:
#                print(f"\t1x {config}")
#            else:
#                clean_runs = [m for m in clean_scores[corpus][config] if m["valid"] == (0, 0)]
#                if len(clean_runs) < 1:
#                    print(f"\t{1 - len(clean_runs)}x {config}")
#
if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
    main(argv)

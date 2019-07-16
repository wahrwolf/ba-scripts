from itertools import product
from functools import reduce
from sys import argv
from os import environ
from os.path import basename
from logging import info, warning, debug, basicConfig
from prettytable import PrettyTable
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
            "start_decay_steps": [None, '21500', '10750', '2500']
        }, "Tagged-cs-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": [None, '21500', '10750', '2500']
        }
    }

LOG_FILES = {
        "Clean-de-en" : [
            "/srv/ftp/share/archive/training/Clean-de-en/logs",
            "/srv/ftp/share/archive/wtmgws2/4dahmen/Clean-de-en/logs",
            "/srv/ftp/share/archive/wtmgws3/data/Clean-de-en/logs",
            "/srv/ftp/share/archive/wtmgws4/data/Clean-de-en/logs",
            "/srv/ftp/share/archive/wtmgws6/4dahmen/Clean-de-en/logs"
        ], "Tagged-de-en" : [
            "/srv/ftp/share/archive/training/Tagged-de-en/logs",
            "/srv/ftp/share/archive/wtmgws2/4dahmen/Tagged-de-en/logs",
            "/srv/ftp/share/archive/wtmgws3/data/Tagged-de-en/logs",
            "/srv/ftp/share/archive/wtmgws4/data/Tagged-de-en/logs",
            "/srv/ftp/share/archive/wtmgws6/4dahmen/Tagged-de-en/logs"
        ], "Clean-cs-en" : [
            "/srv/ftp/share/archive/training/Clean-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws2/4dahmen/Clean-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws3/data/Clean-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws4/data/Clean-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws6/4dahmen/Clean-cs-en/logs"
        ], "Tagged-cs-en" : [
            "/srv/ftp/share/archive/training/Tagged-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws2/4dahmen/Tagged-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws3/data/Tagged-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws4/data/Tagged-cs-en/logs",
            "/srv/ftp/share/archive/wtmgws6/4dahmen/Tagged-cs-en/logs"
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
    """
    Builds dictonary, containng all the configs that are missing in the traingings data.
    Works with mulitple corpora as well!
    """
    missing_configs = {}

    for corpus in schedule:
        if corpus not in trainings_scores:
            warning(f"No entries for corpus {corpus} in reports found! Skipping...")
            continue

        for config in schedule[corpus]:
            # TODO: check if score is 0
            missing_configs[corpus] = [
                config
                for run in trainings_scores[corpus]
                # create dict for comparison without path or scores
                if config in {k:v for k, v in run.items() if k not in ("path", "scores")}
            ]
    return missing_configs

def report_runs(corpora, log_files=LOG_FILES, schedule=HYPER_CONFIGS):
    """
    Prints valid and missing runs from corpora selection
    """
    logs = parse(
                # Load only files from current selection
                [log for corpus, files in log_files.items() for log in files if corpus in corpora]
            )
    results = build_result_table(
                {corpus: configs for corpus, configs in schedule.items() if corpus in corpora},
                logs
            )

    scores = load_scores(results)

    missing_runs = {
        corpus: [
            config
            for run in scores.get(corpus, [])
            # create dict for comparison without path or scores
            if config not in [{k:v for k, v in run.items() if k not in ("path", "scores")}]
        ] for corpus, configs in schedule.items()
            for config in configs
    }

    for corpus in corpora:
        print("Oveview:")
        print("-----------------------")
        for config in schedule[corpus]:
            if config == schedule[corpus][0]:
                trainings_table = PrettyTable(
                    ["corpus"] +
                    list(config.keys()) +
                    [
                        "runs",
                        "score",
                        "path"
                    ])
                trainings_table.align["score"] = "r"
                trainings_table.float_format = "0.3"
            runs = [run
                    for run in scores[corpus]
                        if config == {k:v for k, v in run.items() if k in config}
                        and isinstance(run["scores"]["valid"][1], float)
                    ]
            if runs:
                best_run = reduce(
                    lambda x, y: x if x["scores"]["valid"][1] > y["scores"]["valid"][1] else y,
                    runs)
                trainings_table.add_row(
                    [corpus] +
                    [str(v) for v in config.values()] +
                    [
                        len(runs),
                        best_run['scores']['valid'][1],
                        basename(best_run["path"])
                    ]
                )
            else:
                trainings_table.add_row(
                    [corpus] +
                    [str(v) for v in config.values()] +
                    [
                        len(runs),
                        0.0,
                        "Not found"
                    ]
                )
        print(trainings_table.get_string(sortby="score", reversesort=True))

def main(argv):
    report_runs([corpus for corpus in argv[1:] if corpus in LOG_FILES])

if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
    main(argv)

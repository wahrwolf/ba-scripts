from itertools import product
from functools import reduce
from sys import argv
from os import environ
from os.path import basename, getsize
from yaml import dump
from logging import info, warning, debug, basicConfig
from fire import Fire
from prettytable import PrettyTable
from parse_logs import parse
from stats import calculate_perfect_validation, sizeof_fmt


# list of HYPER_PARAMS
HYPER_PARAMS = {
        "Clean-de-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": ['50000', '9875', '19750']
        }, "Tagged-de-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": ['50000', '9875', '19750']
        }, "Clean-cs-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": ['50000', '21500', '10750']
        }, "Tagged-cs-en": {
            "optim": ["sgd", "adadelta", "adam"],
            "learning_rate": ['1', '0.1', '0.01', '0.001'],
            "start_decay_steps": ['50000', '21500', '10750']
        }
    }


TRAININGS_PARAMS = {
        "Clean-cs-en": {
            "data": "${DATA_DIR}/Clean-cs-en/preprocess/Clean-cs-en",
            "save_model": "${DATA_DIR}/Clean-cs-en/train/Clean-cs-en",
            "gpu_ranks": [0],
            "word_vec_size": 500,
            "encoder_type": "rnn",
            "decoder_type": "rnn",
            "rnn_type": "LSTM",
            "rnn_size": 1000,
            "report_every": 200,
            "batch_size": 32,
            "train_steps": 38700,
            "valid_steps": 1000,
            "valid_batch_size": 16,
            "save_checkpoint_steps": 6450,
            "tensorboard": True,
            "tensorboard_log_dir": "${DATA_DIR}/tensorboard/Clean-cs-en/",
            "warmup_steps": 0
        }, "Tagged-cs-en": {
            "data": "${DATA_DIR}/Tagged-cs-en/preprocess/Tagged-cs-en",
            "save_model": "${DATA_DIR}/Tagged-cs-en/train/Tagged-cs-en",
            "gpu_ranks": [0],
            "word_vec_size": 500,
            "encoder_type": "rnn",
            "decoder_type": "rnn",
            "rnn_type": "LSTM",
            "rnn_size": 1000,
            "report_every": 200,
            "batch_size": 32,
            "train_steps": 38700,
            "valid_steps": 1000,
            "valid_batch_size": 16,
            "save_checkpoint_steps": 6450,
            "tensorboard": True,
            "tensorboard_log_dir": "${DATA_DIR}/tensorboard/Tagged-cs-en/",
            "warmup_steps": 0
        }, "Clean-de-en": {
            "data": "${DATA_DIR}/Clean-de-en/preprocess/Clean-de-en",
            "save_model": "${DATA_DIR}/Clean-de-en/train/Clean-de-en",
            "gpu_ranks": [0],
            "encoder_type": "rnn",
            "decoder_type": "rnn",
            "rnn_type": "LSTM",
            "report_every": 200,
            "rnn_size": 1000,
            "batch_size": 32,
            "train_steps": 35550,
            "valid_steps": 1000,
            "valid_batch_size": 16,
            "save_checkpoint_steps": 11850,
            "tensorboard": True,
            "tensorboard_log_dir": "${DATA_DIR}/tensorboard/Clean-de-en/",
            "warmup_steps": 0,
        }, "Tagged-de-en": {
            "data": "${DATA_DIR}/Tagged-de-en/preprocess/Tagged-de-en",
            "save_model": "${DATA_DIR}/Tagged-de-en/train/Tagged-de-en",
            "gpu_ranks": [0],
            "encoder_type": "rnn",
            "decoder_type": "rnn",
            "rnn_type": "LSTM",
            "report_every": 200,
            "rnn_size": 1000,
            "batch_size": 32,
            "train_steps": 35550,
            "valid_steps": 1000,
            "valid_batch_size": 16,
            "save_checkpoint_steps": 11850,
            "tensorboard": True,
            "tensorboard_log_dir": "${DATA_DIR}/tensorboard/Tagged-de-en/",
            "warmup_steps": 0,
        }
    }

LOG_FILES = {
        "Clean-de-en" : [
            "/srv/ftp/share/archive/results/Clean-de-en/logs",
        ], "Tagged-de-en" : [
            "/srv/ftp/share/archive/results/Tagged-de-en/logs",
            "/srv/ftp/share/archive/training/Tagged-de-en/logs",
        ], "Clean-cs-en" : [
            "/srv/ftp/share/archive/results/Clean-cs-en/logs",
        ], "Tagged-cs-en" : [
            "/srv/ftp/share/archive/results/Tagged-cs-en/logs",
        ]
    }

MODEL_FILES = {
        "Clean-de-en" : [
            "/srv/ftp/share/archive/results/Clean-de-en/data",
        ], "Tagged-de-en" : [
            "/srv/ftp/share/archive/results/Tagged-de-en/data",
            "/srv/ftp/share/archive/training/Tagged-de-en/data",
        ], "Clean-cs-en" : [
            "/srv/ftp/share/archive/results/Clean-cs-en/data",
        ], "Tagged-cs-en" : [
            "/srv/ftp/share/archive/results/Tagged-cs-en/data",
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

def load_scores(result_table, metric, domain):
    for corpus in result_table:
        for run in result_table[corpus]:
            log_file = parse(run["path"])
            scores = calculate_perfect_validation(log_file, corpus, 0)
            run["scores"] = scores
            #sort the entries by validation score in reverese order
        result_table[corpus] = sorted(result_table[corpus], key=lambda run: run["scores"][domain].get(metric,{"score":0})["score"])[::-1]
    return result_table

def build_trainings_config(corpora, log_files=LOG_FILES, schedule=HYPER_CONFIGS, default_params=TRAININGS_PARAMS):
    """
    Builds dictonary, containng all the configs that are missing in the traingings data.
    Works with mulitple corpora as well!
    """
    if isinstance(corpora, str):
        corpora = corpora.split()
    logs = parse(
                # Load only files from current selection
                [log for corpus, files in log_files.items() for log in files if corpus in corpora]
            )
    results = build_result_table(
                {corpus: configs for corpus, configs in schedule.items() if corpus in corpora},
                logs
            )

    scores = load_scores(results, metric, domain)
    missing_configs = {}

    for corpus in corpora:
        for config in schedule[corpus]:
            runs = [run
                    for run in scores[corpus]
                        if config == {k:v for k, v in run.items() if k in config}
                        and isinstance(run["scores"]["valid"][1], float)
                    ]
            if not runs:
                if corpus not in missing_configs:
                    missing_configs[corpus] = []
                missing_configs[corpus].append(config)

    for corpus, configs in missing_configs.items():
        for i, config in enumerate(configs):
            with open(f"train.{corpus}.{i}.config", "w") as config_file:
                dump({**config, **default_params.get(corpus, {})}, config_file)


def show_runs(corpora, log_files=LOG_FILES, metric="valid", domain="mixed"):
    """
    Prints valid and missing runs from corpora selection
    """
    if isinstance(corpora, str):
        corpora = corpora.split()
    logs = parse(
                # Load only files from current selection
                [log for corpus, files in log_files.items() for log in files if corpus in corpora]
            )
    scores = load_scores({corpus: [run["params"] for run in logs[corpus]["train"]] for corpus in logs}, metric, domain)

    params = []
    for corpus in corpora:
        for run in scores[corpus]:
            for param in run:
                if param not in params:
                    params.append(param)
    trainings_table = PrettyTable(
        ["corpus"] +
        [param for param in params if param not in ["corpus", "scores", "path", "size"]] +
        [
            "score",
            "step",
            "path",
            "size"
        ])
    trainings_table.align["score"] = "r"
    trainings_table.align["size"] = "r"
    trainings_table.align["path"] = "l"
    trainings_table.float_format = "0.3"
    for corpus in corpora:
        for run in scores[corpus]:
            trainings_table.add_row(
                [corpus] +
                [run.get(k) for k in params if k not in ["corpus", "scores", "path", "size"]] +
                [
                    run['scores'].get(domain, {}).get(metric, {"score": 0.0})["score"],
                    run['scores'].get(domain, {}).get(metric, {"score": 0.0}).get("step"),
                    basename(run['path']),
                    sizeof_fmt(getsize(run["path"]))
                ])
    print(trainings_table.get_string(sortby="score", reversesort=True))

def show_schedule(corpora, log_files=LOG_FILES, schedule=HYPER_CONFIGS, metric="valid", domain="mixed"):
    """
    Prints valid and missing runs from corpora selection
    """
    if isinstance(corpora, str):
        corpora = corpora.split()
    logs = parse(
                # Load only files from current selection
                [log for corpus, files in log_files.items() for log in files if corpus in corpora]
            )
    results = build_result_table(
                {corpus: configs for corpus, configs in schedule.items() if corpus in corpora},
                logs
            )

    scores = load_scores(results, metric, domain)

    for corpus in corpora:
        for config in schedule[corpus]:
            if config == schedule[corpus][0]:
                trainings_table = PrettyTable(
                    ["corpus"] +
                    list(config.keys()) +
                    [
                        "runs",
                        "score",
                        "step",
                        "path",
                        "size"
                    ])
                trainings_table.align["score"] = "r"
                trainings_table.align["size"] = "r"
                trainings_table.align["path"] = "l"
                trainings_table.float_format = "0.3"
            runs = [run
                    for run in scores[corpus]
                        if config == {k:v for k, v in run.items() if k in config}
                        #and isinstance(run["scores"]["valid"][1], float)
                    ]
            if runs:
                best_run = reduce(
                        lambda x, y:
                            x if
                                x["scores"].get(domain, {}).get(metric, {"score": 0})["score"] >
                                y["scores"].get(domain, {}).get(metric, {"score": 0})["score"]
                            else y,
                    runs)
                trainings_table.add_row(
                    [corpus] +
                    [str(v) for v in config.values()] +
                    [
                        len(runs),
                        best_run['scores'].get(domain, {}).get(metric, {"score": 0.0})["score"],
                        best_run['scores'].get(domain, {}).get(metric, {"score": 0.0}).get("step"),
                        basename(best_run["path"]),
                        sizeof_fmt(getsize(best_run["path"]))
                    ]
                )
            else:
                trainings_table.add_row(
                    [corpus] +
                    [str(v) for v in config.values()] +
                    [
                        len(runs),
                        0,
                        0.0,
                        "Not found",
                        0.0
                    ]
                )
        print(trainings_table.get_string(sortby="score", reversesort=True))

def main(argv):
    show_schedule([corpus for corpus in argv[1:] if corpus in LOG_FILES])
    build_trainings_config([corpus for corpus in argv[1:] if corpus in LOG_FILES])

if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
        Fire({
                "build" : {
                    "configs": build_trainings_config,
                }, "show": {
                    "schedule": show_schedule,
                    "training": show_runs,
                    "log": parse
                }})
    #main(argv)

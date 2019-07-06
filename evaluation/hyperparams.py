from itertools import product
from parse_logs import parse

# list of hyperparams
hyperparams = {
        "optim": ["sgd", "adadelta", "adam"],
        "learning_rate": ['1', '0.1', '0.01', '0.001'],
        "start_decay_steps": [None, '19750', '9875']
    }

log_files = ["/srv/ftp/share/archive/training/Clean-cs-en/logs", "/srv/ftp/share/archive/training/Clean-de-en/logs", "/srv/ftp/share/archive/training/Tagged-cs-en/logs", "/srv/ftp/share/archive/training/Tagged-de-en/logs"]

# build table with possible configs
hyper_configs = [i for i in product(hyperparams["optim"], hyperparams["learning_rate"], hyperparams["start_decay_steps"])]
result_table = {}

# get list of logs
logs = parse(log_files)

for corpus in logs.keys():
    print(f"Corpus: {corpus} with {len(logs[corpus]['train'])}")
    result_table[corpus] = {}
    for config in hyper_configs:
        for run in logs[corpus]["train"]:
            params = run["params"]
            current_config = (params.get("optim", "sgd"), params.get("learning_rate", 1), params.get("start_decay_steps", None))
            if config == current_config:
#                print(f"Found model in {params.get('path')} for {config}")
                result_table[corpus][config] = params["path"]
        if config not in result_table[corpus]:
            print(f"No model found for {config}")


#print(result_table)

# put values into table



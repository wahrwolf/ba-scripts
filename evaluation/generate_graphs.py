from re import compile
from os.path import basename
from math import nan

# prepare 
models = {}
log_files = []
rules = {
        "train": {
            "step" : compile("^.+ Step (?P<step>\d+)/.+ acc: (?P<train_accuracy>.+); ppl: (?P<train_perplexity>.+);.+$)"),
            "valid": compile("^.+ Validation (perplexity: (?P<valid_perplexity>.+)|(accuracy: (?<valid_accuracy>.+))$)")
        }, "config": {
            "corpus": compile("^save_model: ?\"(?P<model_path>.+)\"")
        }, "score": {
            "bleu": compile("")
            }
        }

# get train log files

#

# parse train configurations
for log in log_files:
    # pass over file and try to get the config section
    with open(log) as log_file:
        config = {}
        for line in log_file:
            # apply all regex to each line
            for rule, regex in iter(rules["config"]):
                if regex.match(line):
                    matches = regex.match(line).groupdict()
                    if rule == "corpus":
                        config["corpus"] = basename(matches.get("model_path"))
                    config.update(matches)


    corpus = config.get("corpus")
    models[corpus] = {"param": "", "step" : {}}

    # pass over file again and get all accuracy values
    with open(log) as log_file:
        current_step = {}
        for line in log_file:
            # apply regex to each line
            for rule, regex in iter(rules["train"]):
                if regex.match(line):
                    matches = regex.match(line).groupdict()
                    # if a new value for step is found, add last info to model history
                    if "step" in matches:
                        models[corpus]["step"][matches["step"]] = current_step
                    current_step.update(matches)
                    break



from os import environ
from fire import Fire
from os.path import basename, isfile
from re import compile
from logging import info, warning, debug, basicConfig

RULES = {
        "train": {
            "step" : compile("^.+ Step (?P<step>\d+)/.+ acc: (?P<train_accuracy>.+); ppl: (?P<train_perplexity>.+?);.+"),
            "valid acc": compile("^.+ Validation accuracy: (?P<valid_accuracy>.+)"),
            "valid ppl": compile("^.+ Validation perplexity: (?P<valid_perplexity>.+)")
        }, "config": {
            "model_path": compile("^save_model: ?\"(?P<model_path>.+)\""),
            "optim": compile("optim: \"(?P<optim>.+)\""),
            "learning_rate": compile("learning_rate: (?P<learning_rate>.+)"),
            "start_decay_steps": compile("start_decay_steps: (?P<start_decay_steps>.+)"),
            "corpus": compile("Using config from .+/(?P<corpus>[^/]+)/.+?config$"),
            "type": compile("Using config from .+/(?P<type>[^/]+).+?config$")
        }, "score": {
            "bleu": compile("^BLEU = (?P<BLEU>.+?),.+$")
            }
        }

def extract_config(rules, path):
    with open(path) as log_file:
        config = {}
        for line in log_file:
            # apply all regex to each line
            for rule, regex in rules["config"].items():
                if regex.match(line):
                    matches = regex.match(line).groupdict()
                    config.update(matches)
    return config

def extract_train_stats(rules, config, path):
    """
    Extract training stats with a dict of RegExes into an dict
    """
    model = []
    with open(path) as log_file:
        current_step = {}
        for line in log_file:
            # apply regex to each line
            for rule, regex in rules[config["type"]].items():
                if regex.match(line):
                    debug(f"Rule {rule} matched")
                    matches = regex.match(line).groupdict()
                    debug(f"Found {len(matches)} items in current line")
                    # if a new value for step is found, add last info to model history
                    if "step" in matches:
                        debug("Found next step! Saving previous values")
                        model.append(current_step.copy())
                    current_step.update(matches)
                    break
    return model

def parse(log_files):
    """
    Parse log files and return everything as a dict
    """
    debug(f"Going over {len(log_files)} file...")
    models = {}
    for log in log_files:
        if isfile(log):
            debug(f"Found log '{log}'")
            # pass over file and try to get the config section
            config = extract_config(RULES, log)
            debug("Extracted the following config:")
            debug(config)
            corpus = config.get("corpus")
            models[corpus] = {"param": config, "steps" : extract_train_stats(RULES, config, log)}
        else:
            warning(f"File '{log}' not found!")
    return models

if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
    Fire({"parse": parse, "config": extract_config})

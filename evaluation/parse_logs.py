"""
This script offers some methods to parse logging files.
Thanks to Fire this can also be used directly
"""

from os import environ
from os.path import isfile
import re
from dateutil.parser import parse
from logging import info, warning, debug, basicConfig
from fire import Fire

RULES = {
        "train": {
            "step"      : re.compile("^.+ Step (?P<step>\d+)/.+ acc: (?P<train_accuracy>.+); ppl: (?P<train_perplexity>.+?);.+"),
            "valid acc" : re.compile("^.+ Validation accuracy: (?P<valid_accuracy>.+)"),
            "valid ppl" : re.compile("^.+ Validation perplexity: (?P<valid_perplexity>.+)")
        }, "config": {
            "run"               : re.compile("Testing .+/(?P<run>train.[^/]+)/(?P<model>(?P<corpus>[^/]+)_step_(?P<step>\d+).pt)"),
            "start_time"        : re.compile(r"^\[(?P<start_time>.+) INFO\] Starting training .*"),
            "end_time"          : re.compile(r"^\[(?P<end_time>.+) INFO\] Saving checkpoint .*"),
            "model_path_train"  : re.compile("^save_model: ?\"(?P<model_path>.+)\""),
            "optim"             : re.compile("optim: \"(?P<optim>.+)\""),
            "learning_rate"     : re.compile("learning_rate: (?P<learning_rate>.+)"),
            "start_decay_steps" : re.compile("start_decay_steps: (?P<start_decay_steps>.+)"),
            "corpus_train"      : re.compile("Using config from .+/(?P<corpus>[^/]+)/.+?config$"),
            "type"              : re.compile("Using config from .+/(?P<type>[^/]+).+?config$")
        }, "score": {
            "bleu": re.compile("^BLEU = (?P<BLEU>.+?),.+$")
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
        defaults = ["step"]
        current_step = {k: config.get(k) for k in defaults if k in config}
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
    if isinstance(log_files, list):
        debug(f"Going over {len(log_files)} file...")
    else:
        debug(f"Running in single file mode!")
        log_files = [log_files]

    models = {}
    for log in log_files:
        if isfile(log):
            debug(f"Found log '{log}'")
            # pass over file and try to get the config section
            config = extract_config(RULES, log)
            debug("Extracted the following config:")
            debug(config)
            corpus = config.get("corpus")
            if corpus not in models:
                models[corpus] = []
            models[corpus].append({"params": config, "steps" : extract_train_stats(RULES, config, log)})
        else:
            warning(f"File '{log}' not found!")
    return models

if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
    Fire({"parse": parse, "config": extract_config})

"""
This script offers some methods to parse logging files.
Thanks to Fire this can also be used directly
"""

from os import environ, listdir
from sqlite3 import connect
from os.path import isfile, isdir
import re
from logging import info, warning, debug, basicConfig
from fire import Fire
from tqdm import tqdm

DEFAULT_CONFIG = {
        "train": {
            "optim": "sgd",
            "learning_rate": "1.0",
            "start_decay_steps": "50000",
            }
        }

RULES = {
        "meta": {
            "type"              : re.compile("Using config from .+/(?P<type>[^/]+).+?config$")
            , "train" : {
                "start_time"        : re.compile(r"^\[(?P<start_time>.+) INFO\] Starting training .*"),
                "end_time"          : re.compile(r"^\[(?P<end_time>.+) INFO\] Saving checkpoint .*"),
                "optim"             : re.compile("optim: ?[\"']?(?P<optim>[^\"']+?)[\"']?$"),
                "learning_rate"     : re.compile("learning_rate: ?[\"']?(?P<learning_rate>[^\"']+?)[\"']?$"),
                "start_decay_steps" : re.compile("start_decay_steps: ?[\"']?(?P<start_decay_steps>[^\"']+?)[\"']?$"),
                "corpus_train"      : re.compile("Using config from .+/(?P<corpus>[^/]+)/.+?config$"),
            }, "score" : {
                "start_time"        : re.compile(r"^\[(?P<start_time>.+) INFO\] Translating shard 0."),
                "duration"          : re.compile(r"^Total translation time \(s\): (?P<duration> .+)$"),
                "run"               : re.compile("Testing .+/(?P<run>train.[^/]+)/(?P<model>(?P<corpus>[^/]+)_step_.+.pt)"),
            }, "translate" :{
            }, "preprocess" :{
            }
        }, "body": {
            "train" : {
                "step"      : re.compile("^.+ Step (?P<step>\d+)/.+ acc: (?P<train_accuracy>.+); ppl: (?P<train_perplexity>.+?);.+"),
                "valid acc" : re.compile("^.+ Validation accuracy: (?P<valid_accuracy>.+)"),
                "valid ppl" : re.compile("^.+ Validation perplexity: (?P<valid_perplexity>.+)")
            }, "score" : {
                "bleu": re.compile("^BLEU = (?P<BLEU>.+?),.+$"),
            }, "translate" :{
            }, "preprocess" :{
            }
        }
    }

def extract_config(rules, path):
    with open(path) as log_file:
        config = {"path" : path}
        n_lines = 0
        for line in log_file:
            if rules["meta"]["type"].match(line):
                action_type = rules["meta"]["type"].match(line).groupdict()["type"]
                log_file.seek(0)
                config["type"] = action_type
                break

        for line in log_file:
            n_lines += 1
            config["length"] = n_lines
            for rule, regex in rules["meta"][action_type].items():
                n_lines += 1
                # apply all regex to each line
                if regex.match(line):
                    matches = regex.match(line).groupdict()
                    config.update(matches)
    return {**DEFAULT_CONFIG.get(config.get("type", "train"), {}), **config}
  #  return config

def extract_train_stats(rules, config, path):
    """
    Extract training stats with a dict of RegExes into an dict
    """
    model = []
    with open(path) as log_file:
        current_step = {}
        for line in tqdm(log_file, disable=(__name__ != '__main__'), total=config["length"]):
            # apply regex to each line
            for rule, regex in rules["body"][config["type"]].items():
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

def parse(target_dirs):
    """
    Parse log files and return everything as a dict
    """
    log_files = []
    if isinstance(target_dirs, list):
        debug(f"Going over {len(target_dirs)} directories...")
    else:
        debug(f"Running in single mode!")
        target_dirs = [target_dirs]

    for directory in target_dirs:
        if isdir(directory):
            debug(f"Checking {directory}")
            for log_file in listdir(directory):
                debug(f"-found {log_file}")
                log_files.append(f"{directory}/{log_file}")
        elif isfile(directory):
            debug(f"Target {directory} seems to be a file... Adding it directly")
            log_files.append(directory)


    models = {}
    for log in tqdm(log_files, disable=(__name__ != '__main__')):
        if isfile(log):
            debug(f"Found log '{log}'")
            # pass over file and try to get the config section
            config = extract_config(RULES, log)
            debug("Extracted the following config:")
            debug(config)
            if not all(k in config for k in ["type", "corpus"]):
                debug("Missing some config values! Skipping...")
                continue

            corpus = config.get("corpus")
            if corpus not in models:
                models[corpus] = {}
            if config["type"] not in models[corpus]:
                models[corpus][config["type"]] = []
            models[corpus][config["type"]].append({"params": config, "steps" : extract_train_stats(RULES, config, log)})
        else:
            warning(f"File '{log}' not accesible!")
    return models


if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
    Fire({"parse": parse, "config": extract_config})

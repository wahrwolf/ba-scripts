"""
This script offers some methods to parse logging files.
Thanks to Fire this can also be used directly
"""

from os import environ, listdir
from sqlite3 import connect
from os.path import isfile, isdir, basename, dirname
from os import listdir
from dateutil.parser import parse as read_time
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
#                "word_vector"       : re.compile("^word_vec_size: ?[\"']?(?P<word_vec>[^\"']+?)[\"']?$"),
                "senteces"          : re.compile(r"\[.+ INFO\] number of examples: (?P<examples>\d+)$"),
                "start_decay_steps" : re.compile("start_decay_steps: ?[\"']?(?P<start_decay_steps>[^\"']+?)[\"']?$"),
                "corpus_train"      : re.compile("Using config from .+/(?P<corpus>[^/]+)/.+?config$"),
            }, "score" : {
                "start_time"        : re.compile(r"^\[(?P<start_time>.+) INFO\] Translating shard 0."),
                "duration"          : re.compile(r"^Total translation time \(s\): (?P<duration> .+)$"),
                "run"               : re.compile("Testing .+/(?P<run>train.[^/]+)/(?P<model>(?P<corpus>[^/]+)_step_.+.pt)"),
            }, "translate" :{
            }, "score_file": {
                "step"              : re.compile(r"^(?P<score_type>.+?)-(?P<domain>.+?)-.+?_step_(?P<step>\d*).score$")
            }, "preprocess" :{
            }
        }, "body": {
            "train" : {
                "step"      : re.compile("^.+ Step (?P<step>\d+)/.+ acc: (?P<train_accuracy>.+); ppl: (?P<train_perplexity>.+?);.+"),
                "valid acc" : re.compile("^.+ Validation accuracy: (?P<valid_accuracy>.+)"),
                "valid ppl" : re.compile("^.+ Validation perplexity: (?P<valid_perplexity>.+)")
            }, "score_file" : {
                # for the bleu script (openNMT)
                "bleu": re.compile("^BLEU = (?P<bleu>.+?),.+$"),
                "bleu-lower": re.compile("^LC-BLEU = (?P<bleu_lc>.+?),.+$"),
                # for the google research script
                "rouge1-R":re.compile(r"^rouge1-R,[^,]+,(?P<rouge1_R>[^,]+?),.+$"),
                "rouge1-P":re.compile(r"^rouge1-P,[^,]+,(?P<rouge1_P>[^,]+?),.+$"),
                "rouge1-F":re.compile(r"^rouge1-F,[^,]+,(?P<rouge1_F>[^,]+?),.+$"),
                "rouge2-R":re.compile(r"^rouge2-R,[^,]+,(?P<rouge2_R>[^,]+?),.+$"),
                "rouge2-P":re.compile(r"^rouge2-P,[^,]+,(?P<rouge2_P>[^,]+?),.+$"),
                "rouge2-F":re.compile(r"^rouge2-F,[^,]+,(?P<rouge2_F>[^,]+?),.+$"),
                "rougeL-R":re.compile(r"^rougeL-R,[^,]+,(?P<rougeL_R>[^,]+?),.+$"),
                "rougeL-P":re.compile(r"^rougeL-P,[^,]+,(?P<rougeL_P>[^,]+?),.+$"),
                "rougeL-F":re.compile(r"^rougeL-F,[^,]+,(?P<rougeL_F>[^,]+?),.+$"),
                # for the nlg_eval
                "rouge_L": re.compile(r"ROUGE_L: (?P<rouge_L>.+)$"),
                "bleu_1": re.compile("^Bleu_1: (?P<bleu_1>.+?)$"),
                "bleu_2": re.compile("^Bleu_2: (?P<bleu_2>.+?)$"),
                "bleu_3": re.compile("^Bleu_3: (?P<bleu_3>.+?)$"),
                "bleu_4": re.compile("^Bleu_4: (?P<bleu_4>.+?)$"),
                "meteor": re.compile(r"METEOR: (?P<meteor>.+)$"),
                "cider": re.compile("CIDEr: (?P<cider>.+)$"),
                "stcs": re.compile(r"SkipThoughtsCosineSimilairty: (?P<stcs>.+)$"),
                "eacs": re.compile("EmbeddingAverageCosineSimilairty: (?P<eacs>.+)$"),
                "vecs": re.compile("VectorExtremaCosineSimilarity: (?P<vecs>.+)$"),
                "gms": re.compile("GreedyMatchingScore: (?P<gms>.+)$"),

            }, "score" : {
                "bleu": re.compile("^BLEU = (?P<BLEU>.+?),.+$"),
            }, "translate" :{
            }, "preprocess" :{
            }
        }
    }

def extract_config(rules, path):
    with open(path) as log_file:
        config = {"path": path, "host": basename(path).split("-")[0]}
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
        config["run"] = "{}-train.{}".format(
                config.get("host"),
                read_time(config.get("start_time", "1337-05-04")).strftime("%Y-%m-%dT%H+02:00"))
    return {**DEFAULT_CONFIG.get(config.get("type", "train"), {}), **config}

def extract_scores(rules, config, log_file):
    result_dir = dirname(dirname(log_file))
    data_dir = "{}/data/{}".format(result_dir, config.get("run"))
    scores = []
    if isdir(data_dir):
        for score in listdir(data_dir):
            if not score.endswith(".score"):
                continue
            score_entry = {"run_dir": data_dir, "model": score}
            for rule, regex in rules["meta"]["score_file"].items():
                if regex.match(basename(score)):
                    debug(f"Rule {basename(score)} matched")
                    matches = regex.match(basename(score)).groupdict()
                    debug(f"Found {len(matches)} items in current line")
                    score_entry.update(matches)
            for line in open(f"{data_dir}/{score}"):
                for rule, regex in rules["body"]["score_file"].items():
                    if regex.match(line):
                        debug(f"Rule {line} matched")
                        matches = regex.match(line).groupdict()
                        debug(f"Found {len(matches)} items in current line")
                        score_entry.update(matches)
            scores.append({score_entry["domain"]: score_entry})
        return scores

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
            models[corpus][config["type"]].append(
                    {
                        "params": config,
                        "steps" : extract_train_stats(RULES, config, log),
                        "scores": extract_scores(RULES, config, log)
                    })
        else:
            warning(f"File '{log}' not accesible!")
    return models


if __name__ == '__main__':
    if "LOGGING" in environ:
        basicConfig(level=environ["LOGGING"])
    Fire({"parse": parse, "config": extract_config})

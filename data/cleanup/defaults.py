"""Provide defaults as well as getter for the howl project
"""

from logging import DEBUG
from os import environ

LOGGER_CONFIG = {
    "version" : 1,
    "formatters" : {
        'brief': {'format': '[%(funcName).10s@%(module)s]: %(levelname)-6s %(message)s'}
    }, "handlers" : {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
            'level': DEBUG}
    }, "root" : {
        'handlers': ['console'],
        'level': DEBUG,
    }
}

RUNTIME_OPTIONS = {
        "keep_unaligned" : False,
        "keep_steps" : True,
        "keep_source" : True,
        "first_line" : 0,
        "max_process": None,
        "mode": "line",
        "config" : {
            "path" : "./config.toml",
            },
        "editor" : {
            "encoding" : "utf-8",
            "path" : environ.get("EDITOR", "vi")
            }
        }

def merge_dicts(src_dict, target_dict):
    if not isinstance(src_dict, dict) or not isinstance(target_dict, dict):
        raise TypeError('Params of recursive_update should be dicts')

    merged_dict = {}
    merged_dict.update(src_dict)

    for key in target_dict:
        if isinstance(target_dict[key], dict) and isinstance(
                src_dict.get(key), dict):
            merged_dict[key] = merge_dicts(src_dict[key], target_dict[key])
        else:
            merged_dict[key] = target_dict[key]

    return merged_dict



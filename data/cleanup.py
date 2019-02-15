#!/bin/env python3

from logging import warning, info, debug
from logging.config import dictConfig
from importlib import import_module
from toml import load
from fire import Fire

from cleanup.defaults import merge_dicts, LOGGER_CONFIG as DEFAULT_LOGGER_CONFIG, RUNTIME_OPTIONS as DEFAULT_OPTIONS
from cleanup.plugins.Plugin import Filter, Fixer
from cleanup.corpus import Corpus

def load_plugins(modules_config, options):
    """Loads up all plugins listed in config dict
    """
    info("Loading up plugins:")
    modules = {}
    # Load up modules
    for plugin in modules_config:
        name = plugin['name']
        class_name = plugin['class']
        debug(f"  -Installing: [{name}]")
        try:
            module = import_module(name)
            debug("  -Loaded module")
            class_object = getattr(module, class_name)
            debug("  -Loaded class")

            if ((not Fixer in class_object.__bases__)
                    or (not Filter in class_object.__bases__)):
                raise NotImplementedError
            else:
                debug("  -Plugin-Class is valid!")

        except Exception as err:
            warning(err)
            warning(f"  -Failed to load {name}... Skiping it!")
        else:
            modules[name] = class_object
            info(f"  -Installed {name}")
    return modules

def load_corpora(corpora_config):
    """ Load all corpora from config array
    """
    corpora = {}
    info("Loading up corpora:")
    for corpus in corpora_config:
        name = corpus["name"]
        debug(f"  -Adding {name}")

        try:
            debug(f"  Using: {corpus}")
            corpus_object = Corpus(**corpus)
            debug(f"  -Init succesfull!")
        except Exception as err:
            warning(err)
            warning(f"  -Failed to load {name}... Skiping it!")
        else:
            corpora[name] = corpus_object
            info(f"  -Loaded {name}")
        finally:
            return corpora

def main(config_path=None):
    # Parse config file
    user_config = load(DEFAULT_OPTIONS["options"]["config"]["path"]
                       if config_path is None else config_path)

    runtime_config = merge_dicts(DEFAULT_OPTIONS, user_config.get("options", {}))

    logger_config = merge_dicts(DEFAULT_LOGGER_CONFIG, user_config.get("logger", {}))
    dictConfig(logger_config)

    debug("Loaded the following user config:")
    debug(user_config)

    debug("Expanded the default runtime option")
    debug(DEFAULT_OPTIONS)
    debug(runtime_config)

    debug("Expanded the default logger options")
    debug(DEFAULT_LOGGER_CONFIG)
    debug(logger_config)

    modules = load_plugins(user_config.get("modules", []), runtime_config)
    accounts = load_corpora(user_config.get("corpora", []))

    Fire(accounts)

if __name__ == '__main__':
    main()

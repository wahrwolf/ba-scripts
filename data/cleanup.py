#!/bin/env python3

from fire import Fire
from importlib import import_module
from logging import warning, info, debug
from logging.config import dictConfig
from toml import load
from tempfile import mkdtemp

from cleanup.corpus import Corpus
from cleanup.defaults import merge_dicts, LOGGER_CONFIG as DEFAULT_LOGGER_CONFIG, RUNTIME_OPTIONS as DEFAULT_OPTIONS
from cleanup.plugins.Plugin import Filter, Fixer
from cleanup.recipe import Recipe

def load_plugins(modules_config):
    """Loads up all plugins listed in config dict
    """
    info("Loading up plugins:")
    modules = {}
    # Load up modules
    for plugin in modules_config:
        name = plugin['name']
        class_name = plugin['class']
        module = plugin["module"]
        debug(f"  -Installing: [{name}]")
        try:
            module = import_module(module)
            debug("  -Loaded module")
            class_object = getattr(module, class_name)
            debug("  -Loaded class")

            if ((Fixer in class_object.__bases__)
                    or (Filter in class_object.__bases__)):
                debug("  -Plugin-Class is valid!")
            else:
                raise NotImplementedError("Plugin needs to implement Fixer or Filter!")
        except KeyError as err:
            warning("Could not find param or option:")
            warning(err)
            warning(f"  -Failed to load {name}... Skiping it!")
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
        except KeyError as err:
            warning("Could not find param or option:")
            warning(err)
            warning(f"  -Failed to load {name}... Skiping it!")
        except Exception as err:
            warning(err)
            warning(f"  -Failed to load {name}... Skiping it!")
        else:
            corpora[name] = corpus_object
            info(f"  -Loaded {name}")
    return corpora

def load_recipes(recipe_config, corpora, modules, options):
    """Load all recipes from config array
    """
    recipes = {}

    info("Loading recipes")
    for corpus in recipe_config:
        corpus_name = corpus["corpus"]
        debug(f"  -Creating recipe for {corpus_name}")
        try:
            recipe = corpus["steps"]
            recipe_object = Recipe(corpora[corpus_name], recipe, modules, options)
            debug(f"  -Init succesfull!")
        except KeyError as err:
            warning("Could not find param or option:")
            warning(err)
            warning(f"  -Failed to load {corpus_name}... Skiping it!")
        except Exception as err:
            warning(err)
            warning(f"  -Failed to load {corpus_name}... Skiping it!")
        else:
            recipes[corpus_name] = recipe_object
            info(f"  -Loaded {corpus_name}")
    return recipes

def main(config_path=None):
    # Parse config file
    user_config = load(DEFAULT_OPTIONS["config"]["path"]
                       if config_path is None else config_path)

    runtime_config = merge_dicts(DEFAULT_OPTIONS, user_config.get("options", {}))

    if "target_dir" not in runtime_config:
        debug("Target dir not specified in user config!")
        debug("Creating tempdir...")
        runtime_config["target_dir"] = mkdtemp()
        debug(f"Using {runtime_config['target_dir']}")

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

    modules = load_plugins(user_config.get("modules", []))
    corpora = load_corpora(user_config.get("corpora", []))
    recipes = load_recipes(user_config.get("recipes", []), corpora, modules, runtime_config)

    info("--------------------")
    info("Finished loading up!")

    if runtime_config.get("mode") == "batch":
        for _, recipe in recipes.items():
            recipe.run_steps()
    else:
        Fire({"corpus":corpora, "plugin":modules, "recipe":recipes})

if __name__ == '__main__':
    main()

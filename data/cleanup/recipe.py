"""This is a collection to interact with recpies on corpora
"""
from logging import debug, info, warning
from threading import Thread
from cleanup.defaults import merge_dicts

class Step(Thread):
    def __str__(self):
        return f"'{self.name}'@{self.target_path}"

    def __init__(self, name, plugin, target_path, action, params):
        Thread.__init__(self, name=name)
        self.name = name
        self.plugin = plugin(**params)
        self.target_path = target_path
        self.action = action

    def run(self):
        debug(f"Started new thread for {self}")
        line_number = 0
        with open(self.target_path) as corpus:
            for line in corpus:
                line_number += 1
                if self.plugin.match(line):
                    debug(f"{self.target_path}@{line_number}: {self.name}")
                    if self.action == "report":
                        info(line)
                    elif self.action == "fix":
                        self.plugin.fix_line(line)
                    elif self.action == "edit":
                        self.plugin.edit_line(line)
        debug(f"Finished check on {self}")

class Recipe():
    def __str__(self):
        return str(self.steps)

    def __init__(self, corpus, steps, modules, options):
        self.name = corpus.name
        self.corpus = corpus

        self.steps = []

        info("Adding steps...")
        self.files = []
        for pair, locales in corpus.files.items():
            for locale in locales.values():
                self.files.append(locale)
        debug(f"Using files: {self.files}")

        for step in steps:
            step_name = step["name"]
            debug(f"  -adding {step_name}")
            plugin_name = step["plugin"]
            action_on_match = step.get("action", "report")
            # a plugin may have 0 params
            # in that case none are specified in the config file
            params = merge_dicts(step.get("params", {}), options)
            for locale_file in self.files:
                step_objects = {}
                try:
                    step_object = Step(step_name, modules[plugin_name], locale_file, action_on_match, params)
                    debug(f"  -successfully instanced plugin [{plugin_name}] for {locale_file}")
                except Exception as err:
                    warning(err)
                    warning(f"Could not add init step {step_name} for {locale_file}... Skiping!")
                else:
                    step_objects[locale_file] = step_object
                self.steps.append(step_object)
            debug(f"  -Successfully added '{step_name}'")

        debug("Loaded all steps!")

    def execute(self, pairs=[], locales=[]):
        for step in self.steps:
            info(f"Running '{step}' on {step.target_path}")
            step.start()
        info(f"Started all steps for {self.name}")

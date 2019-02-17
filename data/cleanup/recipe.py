"""This is a collection to interact with recpies on corpora
"""
from logging import debug, info, warning
from threading import Thread

class Step(Thread):
    def __str__(self):
        return self.name

    def __init__(self, name, plugin, target_path, params):
        Thread.__init__(self)
        self.name = name
        self.plugin = plugin(**params)
        self.target_path = target_path

    def run(self):
        debug(f"Started new thread for {self}")
        with open(self.target_path) as corpus:
            for line in corpus:
                if self.plugin.matches_line(line):
                    debug(f"Found line with {self.name}")
                    debug(line)

class Recipe():
    def __str__(self):
        return str(self.steps)

    def __init__(self, corpus, steps, modules):
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
            plugin_name = step["plugin"]
            debug(f"  -adding {step_name}")
            # a plugin may have 0 params
            # in that case none are specified in the config file
            params = step.get("params", {})
            for locale_file in self.files:
                step_objects = {}
                try:
                    step_object = Step(step_name, modules[plugin_name], locale_file, params)
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

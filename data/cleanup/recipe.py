"""This is a collection to interact with recpies on corpora
"""
from logging import debug, info, warning
from threading import Thread

class Step(Thread):
    def __str__(self):
        return self.name

    def __init__(self, name, plugin, params):
        Thread.__init__(self)
        self.name = name
        self.plugin = plugin(**params)

    def run(self, target_file):
        debug(f"Started new thread for {self}")
        for line in target_file.readlines():
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
        for step in steps:
            step_name = step["name"]
            plugin_name = step["plugin"]
            debug(f"  -adding {step_name}")
            # a plugin may have 0 params
            # in that case none are specified in the config file
            params = step.get("params", {})

            try:
                step_object = Step(step_name, modules[plugin_name], params)
                debug(f"  -successfully instanced plugin [{plugin_name}]")
            except Exception as err:
                warning(err)
                warning(f"Could not add init step {step_name}... Skiping!")
            else:
                self.steps.append(step_object)
                debug(f"  -Successfully added '{step_name}'")

        debug("Loaded all steps!")

    def execute(self, pairs=[], locales=[]):
        for step in self.steps:
            corpus_files = self.corpus.files
            info(f"Running '{step}' on {corpus_files}")
            for pair in corpus_files:
                info(f"-Using pair: {pair}")
                for locale in corpus_files[pair]:
                    info(f"-Using locale code: {locale}")
                    file_handle = self.corpus.load_file(pair, locale)
                    step.run(file_handle)

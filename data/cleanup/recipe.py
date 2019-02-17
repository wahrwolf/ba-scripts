"""This is a collection to interact with recpies on corpora
"""
from logging import debug, info, warning
from os import mkdir
from os.path import join, isdir, isfile
from ntpath import basename
from threading import Thread
from cleanup.defaults import merge_dicts

class Step(Thread):
    def __str__(self):
        return f"[{self.name}]@{self.src_file}"

    def __init__(self, name, plugin, src_file, target_file, action, params):
        Thread.__init__(self, name=name)
        self.name = name
        self.plugin = plugin(**params)
        self.src_file = src_file
        self.target_file = target_file
        self.action = action

    def run(self):
        assert isfile(self.src_file), "src_file does not exist!"
        debug(f"Started new thread for {self}")
        line_number = 0
        if self.action == "count":
            lines_matched = 0
        with open(self.target_file, "w+") as target:
            with open(self.src_file) as corpus:
                for line in corpus:
                    line_number += 1
                    if self.plugin.match(line):
                        debug(f"{self}@{line_number}: {self.name}")
                        if self.action == "report":
                            info(line)
                        elif self.action == "fix":
                            self.plugin.fix_line(line)
                        elif self.action == "edit":
                            self.plugin.edit_line(line)
                        elif self.action == "count":
                            lines_matched += 1
                    target.write(line)
        if self.action == "count":
            info(f"{self}: {lines_matched} matches in {line_number} lines")
        debug(f"Finished check on {self}")

class Recipe():
    def __str__(self):
        return str(self.steps)

    def __init__(self, corpus, steps, modules, options):
        self.name = corpus.name
        self.corpus = corpus
        target_dir = options["target_dir"]
        if not isdir(target_dir):
            mkdir(target_dir)

        self.steps = []
        info("Adding steps...")

        self.files = []
        for _, locales in corpus.files.items():
            for locale in locales.values():
                self.files.append(locale)
        debug(f"Using files: {self.files}")

        for step in steps:
            step_name = step["name"]
            debug(f"  -adding {step_name}")
            plugin_name = step["plugin"]
            step_dir = join(target_dir, step_name.replace(" ", "_"))
            if not isdir(step_dir):
                mkdir(step_dir)
            debug(f"  -using '{step_dir}' as workspace")
            action_on_match = step.get("action", "count")
            # a plugin may have 0 params
            # in that case none are specified in the config file
            plugin_params = merge_dicts(step.get("params", {}), {"options":options})
            for i, locale_file in enumerate(self.files):
                src_file = locale_file
                target_file = join(step_dir, basename(src_file))
                step_objects = {}
                try:
                    debug(f"    +'{src_file}' --[{step_name}]--> '{target_file}'")
                    step_object = Step(
                        step_name, modules[plugin_name],
                        src_file, target_file,
                        action_on_match,
                        plugin_params)
                except Exception as err:
                    warning(err)
                    warning(f"Could not init step {step_name} for {src_file}... Skiping!")
                else:
                    self.files[i] = target_file
                    debug(f"  -linked {src_file} to {self.files[i]}")
                    step_objects[locale_file] = step_object
                self.steps.append(step_object)
            debug(f"  -Successfully added '{step_name}'")

        debug("Loaded all steps!")

    def execute(self, pairs=[], locales=[]):
        for step in self.steps:
            info(f"Running {step}")
            step.start()
            #TODO: Align threads to wait for next step
        info(f"Started all steps for {self.name}")

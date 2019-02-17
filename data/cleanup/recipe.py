"""This is a collection to interact with recpies on corpora
"""
from logging import debug, info, warning
from os import mkdir
from os.path import join, isdir, isfile
from ntpath import basename
from multiprocessing.pool import Pool
from cleanup.defaults import merge_dicts

class Step_Runner():
    def __init__(self, recipe, step_id):
        self.step_id = step_id
        self.recipe = recipe
    def __call__(self, task_id):
        self.recipe.run_step(self.step_id, task_id)


class Recipe():
    def __str__(self):
        return str(self.steps)

    def __init__(self, corpus, steps, modules, options):
        self.name = corpus.name
        self.corpus = corpus
        self.options = options
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
            subtasks = []
            for i, locale_file in enumerate(self.files):
                src_file = locale_file
                target_file = join(step_dir, basename(src_file))
                try:
                    debug(f"    +'{src_file}' --[{step_name}]--> '{target_file}'")
                    step_params = {
                        "name": step_name, "plugin": modules[plugin_name],
                        "src_file": src_file, "target_file": target_file,
                        "action":action_on_match, "params": plugin_params}
                except Exception as err:
                    warning(err)
                    warning(f"Could not init step {step_name} for {src_file}... Skiping!")
                else:
                    self.files[i] = target_file
                    debug(f"  -linked {src_file} to {self.files[i]}")
                    subtasks.append(step_params)
            self.steps.append(subtasks)
            debug(f"  -Successfully added '{step_name}'")

        debug("Loaded all steps!")

    def run_step(self, step_id, task_id):
        step_params = self.steps[step_id][task_id]

        name = step_params.get("name")
        plugin = step_params.get("plugin")(**step_params.get("params"))
        src_file = step_params.get("src_file")
        target_file = step_params.get("target_file")
        action = step_params.get("action")

        assert isfile(src_file), "src_file does not exist!"
        debug(f"'{name}'@'{src_file}': Started")
        line_number = 0
        if action == "count":
            lines_matched = 0
        with open(target_file, "w+") as target:
            with open(src_file) as corpus:
                for line in corpus:
                    line_number += 1
                    if plugin.match(line):
                        debug(f"'{name}'@'{src_file}':Found match in line [{line_number}]")
                        if action == "report":
                            info(line)
                        elif action == "fix":
                            plugin.fix_line(line)
                        elif action == "edit":
                            plugin.edit_line(line)
                        elif action == "count":
                            lines_matched += 1
                    target.write(line)
        if action == "count":
            info(f"'{name}'@'{src_file}': {lines_matched} matches in {line_number} lines")
        debug(f"'{name}'@'{src_file}': Finished!")

    def run_steps(self):
        for step_id, step in enumerate(self.steps):
            info(f"Running {step}")
            with Pool(self.options.get("max_processes")) as pool:
                step_report = pool.map(Step_Runner(self, step_id), [task_id for task_id, _ in enumerate(step)])
        info(f"Started all steps for {self.name}")

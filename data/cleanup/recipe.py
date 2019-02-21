"""This is a collection to interact with recpies on corpora
"""
from functools import reduce
from logging import debug, info, warning
from multiprocessing.pool import Pool
from ntpath import basename
from os import mkdir, rename, remove
from os.path import join, isdir
from shutil import copyfile

from cleanup.defaults import merge_dicts

class StepRunner():
    """Helper class to run a step in a new process
    """
    def __init__(self, recipe, step_id):
        self.step_id = step_id
        self.recipe = recipe

    def run(self, task_id):
        """Helper function to run a steop in a process
        """
        return self.recipe.run_step(self.step_id, task_id)

    def align(self, task_id, lines):
        """Helper function to remove lines from a file in a process
        """
        return self.recipe.remove_lines(self.step_id, task_id, lines)

class Recipe():
    """Collection of steps to prepare a text corpus
    Use run_step or run_steps to execute the preprocessing
    """
    def __str__(self):
        return str(self.steps)

    def __init__(self, corpus, steps, modules, options):
        self.name = corpus.name
        self.corpus = corpus
        self.options = options

        info(f"Creating recipe for {corpus.name}")

        target_dir = options["target_dir"]
        if not isdir(target_dir):
            mkdir(target_dir)

        self.steps = []
        self.files = []

        for pair, locales in corpus.files.items():
            for locale_code, data_file in locales.items():
                self.files.append({
                    "src_file":data_file,
                    "pair": pair,
                    "code": locale_code})
        debug(f"Using files: {self.files}")

        for step in steps:
            step_name = step["name"]
            debug(f"  -adding {step_name}")

            plugin_name = step["plugin"]
            plugin_params = merge_dicts(step.get("params", {}), {"options":options})
            debug(f"  -using plugin: [{plugin_name}] with")
            debug(f"  {plugin_params}")

            step_dir = join(target_dir, step_name.replace(" ", "_"))
            if not isdir(step_dir):
                mkdir(step_dir)
            debug(f"  -using '{step_dir}' as workspace")

            action_on_match = step.get("action", "count")
            # a plugin may have 0 params
            # in that case none are specified in the config file
            subtasks = []
            for i, locale in enumerate(self.files):
                target_file = join(step_dir, basename(locale["src_file"]))
                step_locale = merge_dicts(locale, {"target_file": target_file})
                debug(f"    +loading step for {step_locale}")
                try:
                    debug(f"    +'{step_locale['src_file']}' --[{step_name}]--> '{step_locale['target_file']}'")
                    step_params = {
                        "name": step_name,
                        "locale": step_locale,
                        "plugin": modules[plugin_name], "params": plugin_params,
                        "action":action_on_match}
                except Exception as err:
                    warning(err)
                    warning(f"Could not init step '{step_name}' for '{locale['src_file']}'... Skiping!")
                else:
                    self.files[i] = merge_dicts(locale, {"src_file":target_file})
                    debug(f"  -linked {locale['src_file']} to {self.files[i]['src_file']}")
                    subtasks.append(step_params)
            self.steps.append(subtasks)

        debug("Loaded all steps!")

    def remove_lines(self, step_id, task_id, removable_lines):
        """Run one step from the preprocessing pipeline.
        This can be done to repeat a filter (e.g. with different action)
        without having to rerun the whole pipeline
        """
        step_params = self.steps[step_id][task_id]


        try:
            name = "Allign corpus"

            locale = step_params["locale"]
            locale_code = locale["code"]
            src_file = f"{locale['target_file']}.unaligned"
            target_file = locale["target_file"]
            pair = locale["pair"]

            excluded_lines = removable_lines.get(pair, [])

            info(f"  -Started task {task_id} to allign {pair}/{locale_code}")
        except KeyError as err:
            debug(f"  -[{pair}/{locale_code}]: Argument missing!")
            debug(err)
            raise err
        else:
            if not excluded_lines:
                if not self.options.get("keep_unaligned", False):
                    rename(src_file, target_file)
                    debug(f"  -[{pair}/{locale_code}]': {src_file} --(mv)--> {target_file}")
                else:
                    copyfile(src_file, target_file)
                    debug(f"  -[{pair}/{locale_code}]': {src_file} --(cp)--> {target_file}")
                return
            debug(f"  -[{pair}/{locale_code}]': {src_file} --(=-{len(excluded_lines)})--> {target_file}")

        line_number = self.options["first_line"]
        with open(target_file, "w+") as target:
            with open(src_file) as corpus:
                for line in corpus:
                    if not line_number in excluded_lines:
                        target.write(line)
                    else:
                        debug(f"  -[{pair}/{locale_code}]: deleted line [{src_file}:{line_number}]")
                    line_number += 1
        if not self.options.get("keep_unaligned", False):
            remove(src_file)
            debug(f"  -[{pair}/{locale_code}]: Deleting tmp file '{src_file}'")
        else:
            debug(f"  -[{pair}/{locale_code}]: Keeping tmp file '{src_file}'")

    def run_step(self, step_id, task_id):
        """Run one step from the preprocessing pipeline.
        This can be done to repeat a filter (e.g. with different action)
        without having to rerun the whole pipeline
        """
        step_params = self.steps[step_id][task_id]

        try:
            name = step_params["name"]

            plugin_params = step_params["params"]
            plugin = step_params["plugin"](**plugin_params)

            locale = step_params["locale"]
            locale_code = locale["code"]
            src_file = locale["src_file"]
            target_file = f"{locale['target_file']}.unaligned"
            pair = locale["pair"]

            action = step_params["action"]

            info(f"  -Started task {task_id} as {name} on {pair}/{locale_code}")
        except KeyError as err:
            debug(f"  -[{pair}/{locale_code}]: Argument missing!")
            debug(err)
            raise err
        else:
            debug(f"  -[{pair}/{locale_code}]': {src_file} --{action}--> {target_file}")

        line_number = self.options["first_line"]
        if action == "count":
            lines_matched = 0
        deleted_lines = set()
        with open(target_file, "w+") as target:
            with open(src_file) as corpus:
                for line in corpus:
                    matches = plugin.match(line)
                    if matches:
                        debug(f"  -[{pair}/{locale_code}]: Found match in [{src_file}:{line_number}]")
                        debug(f"  -[{pair}/{locale_code}]: {matches}")
                        if action == "report":
                            info(line)
                        elif action == "fix":
                            line = plugin.fix_line(line)
                        elif action == "edit":
                            line = plugin.edit_line(line)
                        elif action == "count":
                            lines_matched += 1
                        elif action == "delete":
                            deleted_lines.add((pair, line_number))
                    line_number += 1
                    target.write(line)

        if not self.options.get("keep_steps", True):
            if step_id == 0 and self.options.get("keep_source", True):
                debug(f"  -[{pair}/{locale_code}]: Keeping source '{src_file}'")
            else:
                debug(f"  -[{pair}/{locale_code}]: Deleting tmp file '{src_file}'")
                remove(src_file)
        else:
            debug(f"  -[{pair}/{locale_code}]: Keeping tmp file '{src_file}'")

        if action == "count":
            info(f"  -[{pair}/{locale_code}]: " +
                 f"Found {lines_matched} ({lines_matched/line_number *100:.2f}%) " +
                 f"matches in {line_number} lines")
        elif action == "delete":
            info(f"  -[{pair}/{locale_code}]: " +
                 f"Found {len(deleted_lines)} ({len(deleted_lines)/line_number *100:.2f}%) " +
                 f"deleted in {line_number} lines")
        debug(f"  -[{pair}/{locale_code}]: Finished!")
        return deleted_lines

    def run_steps(self):
        """Run the whole preprocessing pipeline using subprocesses
        """
        for step_id, step in enumerate(self.steps):
            with Pool(self.options.get("max_processes")) as pool:
                info(f"Running step {step_id}")
                worker_list = [task_id for task_id, _ in enumerate(step)]
                step_report = pool.map(StepRunner(self, step_id).run, worker_list)
                misaligned_lines = reduce(lambda x, y: x|y, step_report) # merge sets
                debug(f"Found {len(misaligned_lines)} misaligned lines!")

                removable_lines = {}
                for pair, line_number in misaligned_lines:
                    if not pair in removable_lines:
                        removable_lines[pair] = []
                    removable_lines[pair].append(line_number)

                info(f"Realigning lines {step_id}")
                worker_list = [(wid, removable_lines) for wid in worker_list]
                step_report = pool.starmap(StepRunner(self, step_id).align, worker_list)

        info(f"Finished all steps for {self.name}")

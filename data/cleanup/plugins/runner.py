"""Module to run executables as a plugin
"""
from os.path import isfile
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
from logging import debug, info, warning

from cleanup.defaults import merge_dicts
from .Plugin import Filter, Fixer

class IORunner(Fixer):
    """Use external program as a filter
    """

    def __init__(self, options, argv, env=None, shell=True, timeout=None, working_directory=None, capture="stdout"):
        debug(f"Creating instance of [{self.__class__.__name__}]")

        assert shell or isfile(argv[0]), "Could not find executable!"

        self.capture = capture
        if options["mode"] == "line":
            debug(f"  -spining up process:")
            debug(f"  {argv}")
            if capture == "stdout":
                stdout = PIPE
                stderr = None
            elif capture == "stderr":
                stdout = None
                stderr = PIPE
            else:
                self.capture = "stdout"
                stdout = PIPE
                stderr = STDOUT

            process = Popen(
                args=argv, env=env, shell=shell, cwd=working_directory,
                stdin=PIPE, stdout=stdout, stderr=stderr,
                encoding="utf8"
                )
            if not process.poll():
                debug(f"  -Process ready for filter!")
            else:
                raise Exception(f"Process exited with [{process.returncode}]")
            self.process = process
        else:
            self.subprocess_args = {
                "args":argv, "env":env, "shell":shell, "cwd":working_directory,
                "encoding": None
                }
            self.timeout = timeout

    def fix_line(self, pair, code, line, line_number):
        self.process.stdin.write(line)
        self.process.stdin.flush()

        if self.capture == "stderr":
            return self.process.stderr.write(line)

        return self.process.stdout.readline()

    def match(self, pair, code, line, line_number):
        assert isinstance(line, str), "Line has to be a string"

        return True


    def fix_file(self, corpus, pair, locale_code, src_file, target_file, action):
        """Run whole file through external binary
        You can use {corpus}, {pair}, {locale_code}, {src_file}, {target_file} in the args
        """
        current_argdict = {}
        if self.capture == "stderr":
            current_argdict["stderr"] = open(target_file, "w+")
            current_argdict["stdout"] = None
        elif self.capture == "stdout":
            current_argdict["stderr"] = None
            current_argdict["stdout"] = open(target_file, "w+")
        else:
            current_argdict["stderr"] = STDOUT
            current_argdict["stdout"] = open(target_file, "w+")
        current_argdict["stdin"] = open(src_file)

        current_argdict["args"] = []

        if isinstance(self.subprocess_args, dict):
            template_arg = self.subprocess_args["args"][pair][locale_code]
        else:
            template_arg = self.subprocess_args["args"]

        for arg, expand in template_arg:
            if expand:
                current_argdict["args"].append(arg.format(**{"corpus":corpus, "pair":pair, "locale_code": locale_code,
                                       "src_file": src_file, "target_file":target_file}))

        debug(f"  -[{pair}/{locale_code}]: Started external {current_argdict['args'][0]}")
        process = Popen(**merge_dicts(self.subprocess_args, current_argdict))
        
        try:
            process.wait(self.timeout)
        except TimeoutExpired as err:
            process.kill()
            warning(f"  -[{pair}/{locale_code}]: Timeout occured for {current_argdict['args'][0]}")
            raise err
        else:
            debug(f"  -[{pair}/{locale_code}]: finished with [{process.returncode}]")
            return set()


from logging import debug, info, warning
from subprocess import call
from tempfile import NamedTemporaryFile

class Filter:
    """Interface class that all filter plugins need to implement
    """
    def __init__(self, options):
        self.runtime_config = options

    def match(self, pair, code, line):
        """abstract method
        returns a bool
        """
    def edit_line(self, line):
        tmp_file = NamedTemporaryFile("w")
        editor = self.runtime_config["editor"]["path"]
        editor_cmd = f"{editor} {tmp_file.name}"
        debug(editor_cmd)
        try:
            tmp_file.write(line)
            tmp_file.flush()
            return_code = call(editor_cmd, shell=True)
            if return_code == 0:
                tmp_file.seek()
                raw_line = tmp_file.file.read()
                line = raw_line.decode("utf-8").replace('\n', '')
        except Exception as err:
            warning(f"Unable to edit line!")
            warning(err)
        finally:
            return line

class Fixer(Filter):
    """Interface class that all fixer plugins need to implement
    """

    def fix_line(self, pair, code, line_number, line):
        """abstract method to
        """

    def fix_file(self, pair, locale_code, src_file, target_file, action):
        """abstract method to fix a file
        returns: set of deleted lines as pairs
        """

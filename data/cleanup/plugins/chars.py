"""Collection of plugins for character manipulation
"""

from re import compile as build_regex
from logging import debug, info
from .Plugin import Filter, Fixer

class InvalidChar(Fixer):
    """Find invalid chars
    """

    def __init__(self, chars, options, replace_dict=None):
        debug(f"Creating instance of [{self.__class__.__name__}]")
        self.invalid_chars = chars
        self.runtime_config = options

        if not replace_dict is None:
            self.replace_dict = replace_dict
            debug("  -Found replacement dict")

        self.regex = build_regex(f"([{''.join(chars)}])")
        debug(f"  -Using regex '{self.regex.pattern}'")

    def match(self, pair, code, line):
        """Check if line contains invalid char.
        Returns bool
        """
        assert isinstance(line, str), "Line has to be a string"
        matches = self.regex.findall(line)

        return matches

    def fix_line(self, pair, code, line_number, line):
        """Fixes line by replacing all chars with corresponding string from dict
        """
        assert isinstance(line, str), "Line has to be a string"
        assert not self.replace_dict is None, "No replace dict specified"

        line.translate(self.replace_dict)

        return line

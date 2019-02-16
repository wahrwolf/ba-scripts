"""Collection of plugins for character manipulation
"""

from re import compile as build_regex
from logging import debug, info
from .Plugin import Filter, Fixer

class InvalidChar(Fixer):
    """Find invalid chars
    """

    def __init__(self, char, replace_dict=None):
        if isinstance(char, list):
            self.invalid_chars = char
        elif isinstance(char, str):
            self.invalid_chars = list(char)
        else:
            self.invalid_chars = [char]

        if not replace_dict is None:
            self.replace_dict = replace_dict

    def matches_line(self, line):
        """Check if line contains invalid char.
        Returns bool
        """
        assert isinstance(line, str), "Line has to be a string"
        regex = build_regex(f"([{str(self.invalid_chars)}])")
        matches = regex.match(line)

        if not matches is None:
            debug(line)
            debug("Found: {matches}")
            return matches
        else:
            return False




    def fix_line(self, line):
        """Fixes line by replacing all chars with corresponding string from dict
        """
        assert isinstance(line, str), "Line has to be a string"
        assert not self.replace_dict is None, "No replace dict specified"

        line.translate(self.replace_dict)

        return line

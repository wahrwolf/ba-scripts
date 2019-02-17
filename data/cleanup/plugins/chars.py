"""Collection of plugins for character manipulation
"""

from re import compile as build_regex
from logging import debug, info
from .Plugin import Filter, Fixer

class InvalidChar(Fixer):
    """Find invalid chars
    """

    def __init__(self, chars, replace_dict=None):
        self.invalid_chars = chars

        if not replace_dict is None:
            self.replace_dict = replace_dict

        self.regex = build_regex(f"({''.join(chars)})")
        debug(f"Initialized with: {self.regex}")

    def matches_line(self, line):
        """Check if line contains invalid char.
        Returns bool
        """
        assert isinstance(line, str), "Line has to be a string"
        matches = self.regex.match(line)

        if not matches is None:
            debug(line)
            debug(f"Found: {matches}")
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

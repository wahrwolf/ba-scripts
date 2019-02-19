"""Collection of plugins for string manipulation
"""
from re import compile as build_regex
from logging import debug, info
from .Plugin import Filter, Fixer

class StringRegex(Fixer):
    """Find invalid chars
    """

    def __init__(self, options, match_pattern, fix_replace="", fix_pattern=None):
        debug(f"Creating instance of [{self.__class__.__name__}]")
        self.runtime_config = options

        self.match_regex = build_regex(match_pattern)
        debug(f"  -Using match patern '{self.match_regex.pattern}'")

        if not fix_pattern is None:
            self.fix_regex = build_regex(fix_pattern)
        else:
            self.fix_regex = build_regex(match_pattern)
        debug(f"  -Using fix patern '{self.fix_regex.pattern}'")

        self.fix_replace = fix_replace
        debug(f"  -Using fix patern '{self.fix_replace}'")

    def match(self, line):
        """Check if line matches pattern
        Returns bool
        """
        assert isinstance(line, str), "Line has to be a string"
        matches = self.match_regex.findall(line)

        return matches

    def fix_line(self, line):
        """Fixes line by applying pattern
        """
        assert isinstance(line, str), "Line has to be a string"

        return self.fix_regex.sub(self.fix_replace, line)

"""Collection of plugins for string manipulation
"""
import operator
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

class StringCounter(Filter):
    """Regex plugin, that only matches if a regex matches a certain amount of times
    """
    def __init__(self, options, match_pattern, match_operator, count):
        debug(f"Creating instance of [{self.__class__.__name__}]")
        self.runtime_config = options

        self.regex = build_regex(match_pattern)
        debug(f"  -Using match patern '{self.regex.pattern}'")

        operators = {
            "<": operator.lt,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            ">=": operator.ge,
            ">": operator.gt
                }
        self.operator = operators[match_operator]
        self.count = count
        debug(f"  -Checking if len(matches) {self.operator} {self.count}")

    def match(self, line):
        assert isinstance(line, str), "Line has to be a string"
        matches = self.regex.findall(line)

        return self.operator(len(matches), self.count)

class StringCompare(Filter):
    """Regex plugin, that only matches if a regex matches a certain amount of times
    """
    def __init__(self, options, pattern_a, pattern_b, match_operator):
        debug(f"Creating instance of [{self.__class__.__name__}]")
        self.runtime_config = options

        self.regex_a = build_regex(pattern_a)
        debug(f"  -Using match patern '{self.regex_a.pattern}'")

        self.regex_b = build_regex(pattern_b)
        debug(f"  -Using match patern '{self.regex_b.pattern}'")

        operators = {
            "<": operator.lt,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            ">=": operator.ge,
            ">": operator.gt
                }
        self.operator = operators[match_operator]
        debug(f"  -Checking if A {self.operator} B")

    def match(self, line):
        assert isinstance(line, str), "Line has to be a string"
        matches_a = self.regex_a.findall(line)
        matches_b = self.regex_b.findall(line)

        return self.operator(len(matches_a), len(matches_b))

"""Collection of plugins to certain lines
"""
from random import seed, sample
from logging import debug, info
from .Plugin import Filter, Fixer


class RandomPicker(Filter):
    """Picks random lines
    """
    def __init__(self, options, init_seed, count, line_max, line_min=None):
        debug(f"Creating instance of [{self.__class__.__name__}]")
        self.runtime_options = options
        debug(f"  -Using [{init_seed}] as seed")
        seed(init_seed)

        if line_min is None:
            line_min = options["first_line"]

        debug(f"  -Using a selection of {count} lines for [{line_min}..{line_max}]")
        self.included_line_numbers = sample(range(line_min, line_max), k=count)


    def match(self, pair, code, line, line_number):
        return line_number not in self.included_line_numbers

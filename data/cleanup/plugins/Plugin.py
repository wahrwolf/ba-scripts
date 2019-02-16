
class Filter:
    """Interface class that all filter plugins need to implement
    """
    def matches_line(self, line):
        """abstract method
        returns a bool
        """

class Fixer(Filter):
    """Interface class that all fixer plugins need to implement
    """

    def fix_line(self, line):
        """abstract method to
        """


class Filter:
    """Interface class that all filter plugins need to implement
    """
    def matches_line(self, line):
        """abstract method
        returns a bool
        """

class Fixer:
    """Interface class that all fixer plugins need to implement
    """
    def needs_fixing(self, line):
        """abstract method to check if a line is applicable for fixing
        returns a bool
        """

    def fix_line(self, line):
        """abstract method to
        """

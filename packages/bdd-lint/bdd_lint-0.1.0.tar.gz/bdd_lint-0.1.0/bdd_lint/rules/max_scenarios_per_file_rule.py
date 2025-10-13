from .base_rule import BaseRule

class MaxScenariosPerFileRule(BaseRule):
    """
    Flags if the number of scenarios in a file exceeds a threshold (default 10).
    """
    def __init__(self, max_scenarios=10):
        self.max_scenarios = max_scenarios
        self.count = 0
    def check(self, scenario):
        self.count += 1
        issues = []
        if self.count > self.max_scenarios:
            issues.append(f"Too many scenarios in file (>{self.max_scenarios})")
        return issues

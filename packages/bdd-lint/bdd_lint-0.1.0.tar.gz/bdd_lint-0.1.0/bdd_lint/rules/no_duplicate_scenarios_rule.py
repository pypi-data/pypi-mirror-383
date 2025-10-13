from .base_rule import BaseRule

class NoDuplicateScenariosRule(BaseRule):
    """
    Flags duplicate scenario names within a feature file.
    """
    def __init__(self):
        self.seen = set()
    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', '').strip()
        if scenario_name in self.seen:
            issues.append(f"Duplicate scenario name: {scenario_name}")
        self.seen.add(scenario_name)
        return issues

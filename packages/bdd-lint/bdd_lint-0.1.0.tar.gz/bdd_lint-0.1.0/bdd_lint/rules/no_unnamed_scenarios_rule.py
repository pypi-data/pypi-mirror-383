from .base_rule import BaseRule

class NoUnnamedScenariosRule(BaseRule):
    """
    Flags scenarios without a name.
    """
    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', '').strip()
        if not scenario_name or scenario_name == 'Scenario:':
            issues.append("Scenario is unnamed.")
        return issues

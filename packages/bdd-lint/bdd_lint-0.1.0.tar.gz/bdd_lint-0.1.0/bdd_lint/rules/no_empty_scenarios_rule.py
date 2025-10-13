from .base_rule import BaseRule

class NoEmptyScenariosRule(BaseRule):
    """
    Flags scenarios that have no steps.
    """
    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', 'Unnamed Scenario')
        steps = scenario.get('steps', [])
        if not steps:
            issues.append(f"{scenario_name}: Scenario has no steps.")
        return issues

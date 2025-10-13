from .base_rule import BaseRule

class LowerCaseScenarioNameRule(BaseRule):
    """
    Enforces scenario names to be lower case.
    """
    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', '')
        if scenario_name and scenario_name != scenario_name.lower():
            issues.append(f"Scenario name should be lower case: {scenario_name}")
        return issues

from .base_rule import BaseRule

class NoScenarioOutlinesWithoutExamplesRule(BaseRule):
    """
    Flags scenario outlines that do not have an Examples section.
    """
    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', '').strip().lower()
        if 'scenario outline:' in scenario_name:
            if not scenario.get('examples'):
                issues.append(f"{scenario['name']}: Scenario Outline missing Examples section.")
        return issues

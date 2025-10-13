from bdd_lint.rules.base_rule import BaseRule

class OneWhenThenRule(BaseRule):
    """
    Restricts each scenario to exactly one When and one Then step.
    """
    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', 'Unnamed Scenario')
        steps = scenario.get('steps', [])
        if not isinstance(steps, list):
            return [f"{scenario_name}: Steps are not a list."]
        when_count = sum(1 for step in steps if step.strip().lower().startswith('when'))
        then_count = sum(1 for step in steps if step.strip().lower().startswith('then'))
        if when_count != 1:
            issues.append(f"{scenario_name}: Step: 'When' - Scenario must contain exactly one When step (found {when_count}).")
        if then_count != 1:
            issues.append(f"{scenario_name}: Step: 'Then' - Scenario must contain exactly one Then step (found {then_count}).")
        return issues
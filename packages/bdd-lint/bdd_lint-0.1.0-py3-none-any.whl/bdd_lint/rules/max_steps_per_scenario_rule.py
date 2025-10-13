from .base_rule import BaseRule

class MaxStepsPerScenarioRule(BaseRule):
    """
    Flags if the number of steps in a scenario exceeds a threshold (default 10).
    """
    def __init__(self, max_steps=10):
        self.max_steps = max_steps
    def check(self, scenario):
        issues = []
        steps = scenario.get('steps', [])
        if len(steps) > self.max_steps:
            issues.append(f"Too many steps in scenario (>{self.max_steps})")
        return issues

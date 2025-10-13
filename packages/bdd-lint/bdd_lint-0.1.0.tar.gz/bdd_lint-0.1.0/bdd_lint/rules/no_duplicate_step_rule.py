from .base_rule import BaseRule

class NoDuplicateStepRule(BaseRule):
    """
    Flags duplicate steps within a scenario.
    """
    def check(self, scenario):
        issues = []
        steps = scenario.get('steps', [])
        seen = set()
        for step in steps:
            if step in seen:
                issues.append(f"Duplicate step: {step}")
            seen.add(step)
        return issues

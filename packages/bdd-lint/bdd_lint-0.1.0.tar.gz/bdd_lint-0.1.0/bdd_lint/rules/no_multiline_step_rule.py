from .base_rule import BaseRule

class NoMultilineStepRule(BaseRule):
    """
    Flags steps that span multiple lines.
    """
    def check(self, scenario):
        issues = []
        steps = scenario.get('steps', [])
        for step in steps:
            if '\n' in step:
                issues.append(f"Multiline step detected: {step}")
        return issues

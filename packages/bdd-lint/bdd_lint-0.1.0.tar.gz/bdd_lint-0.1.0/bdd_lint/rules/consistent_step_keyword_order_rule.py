from .base_rule import BaseRule

class ConsistentStepKeywordOrderRule(BaseRule):
    """
    Ensures step keywords appear in the order: Given, When, Then.
    """
    def check(self, scenario):
        issues = []
        steps = scenario.get('steps', [])
        order = ['given', 'when', 'then']
        found = []
        for step in steps:
            for keyword in order:
                if step.strip().lower().startswith(keyword):
                    found.append(keyword)
        if found != sorted(found, key=lambda x: order.index(x)):
            issues.append(f"Step keywords are out of order: {found}")
        return issues

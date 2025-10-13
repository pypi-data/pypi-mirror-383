from .base_rule import BaseRule

class ThenFutureTenseRule(BaseRule):
    """
    Enforces future verbs (should, will, shall) for 'Then' steps in BDD scenarios.
    """
    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', 'Unnamed Scenario')
        steps = scenario.get('steps', [])
        if not isinstance(steps, list):
            return [f"{scenario_name}: Steps are not a list."]
        for step in steps:
            step_text = step.strip()
            if step_text.lower().startswith('then'):
                modal_verbs = ["should", "will", "shall"]
                if not any(modal in step_text.lower() for modal in modal_verbs):
                    issues.append(f"{scenario_name}: Step: '{step_text}' - Should use a future verb (should, will, shall).")
        return issues

from .base_rule import BaseRule
from bdd_lint.utils.nlp import is_present


class WhenPresentTenseRule(BaseRule):
    """Enforces present tense for 'When' steps in BDD scenarios."""

    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', 'Unnamed Scenario')
        steps = scenario.get('steps', [])
        if not isinstance(steps, list):
            return [f"{scenario_name}: Steps are not a list."]
        for step in steps:
            step_text = step.strip()
            if step_text.lower().startswith('when'):
                if not is_present(step_text):
                    issues.append(f"{scenario_name}: Step: '{step_text}' - Should use present tense.")
        return issues

from .base_rule import BaseRule
from bdd_lint.utils.nlp import is_past


class GivenPastTenseRule(BaseRule):
    """Enforces past tense for 'Given' steps in BDD scenarios.

    Uses a lightweight helper which falls back to heuristics when heavy NLP
    packages are not installed. This makes unit tests deterministic.
    """

    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', 'Unnamed Scenario')
        steps = scenario.get('steps', [])
        if not isinstance(steps, list):
            return [f"{scenario_name}: Steps are not a list."]
        for step in steps:
            step_text = step.strip()
            if step_text.lower().startswith('given'):
                if not is_past(step_text):
                    issues.append(f"{scenario_name}: Step: '{step_text}' - Should use past tense.")
        return issues
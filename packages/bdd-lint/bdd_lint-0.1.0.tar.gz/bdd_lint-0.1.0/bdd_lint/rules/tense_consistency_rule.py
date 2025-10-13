from .base_rule import BaseRule
from bdd_lint.utils.nlp import detect_tense


class TenseConsistencyRule(BaseRule):
    """Allows either all-present tense or past-present-future for Given-When-Then.

    Uses `detect_tense` helper that falls back to heuristics for reproducible tests.
    """

    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', 'Unnamed Scenario')
        steps = scenario.get('steps', [])
        if not isinstance(steps, list):
            return [f"{scenario_name}: Steps are not a list."]
        tense_map = {}
        for step in steps:
            step_text = step.strip()
            step_type = None
            if step_text.lower().startswith('given'):
                step_type = 'Given'
            elif step_text.lower().startswith('when'):
                step_type = 'When'
            elif step_text.lower().startswith('then'):
                step_type = 'Then'
            if step_type:
                tense = detect_tense(step_text)
                tense_map[step_type] = tense
        # When all detected as present
        if tense_map and set(tense_map.values()) == {'present'}:
            return []
        # Allow Given-past, When-present, Then-future or present
        if (
            tense_map.get('Given') == 'past'
            and tense_map.get('When') == 'present'
            and tense_map.get('Then') in {'future', 'present'}
        ):
            return []
        expected = (
            "Expected formats: (1) All steps in present tense OR (2) Given in past, When in present, Then in future."
        )
        if tense_map:
            issues.append(f"{scenario_name}: Step: tenses are inconsistent or mixed. Detected: {tense_map}. {expected}")
        return issues

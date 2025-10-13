from .base_rule import BaseRule

class ThirdPersonRule(BaseRule):
    """
    Enforces that all Gherkin steps use third-person perspective (no first- or second-person pronouns).
    """
    FIRST_PERSON = {"i", "we", "me", "my", "mine", "our", "ours"}
    SECOND_PERSON = {"you", "your", "yours"}

    def check(self, scenario):
        issues = []
        scenario_name = scenario.get('name', 'Unnamed Scenario')
        steps = scenario.get('steps', [])
        if not isinstance(steps, list):
            return [f"{scenario_name}: Steps are not a list."]
        for step in steps:
            step_text = step.strip().lower()
            words = set(step_text.split())
            if words & self.FIRST_PERSON:
                issues.append(f"{scenario_name}: Step: '{step_text}' - Should use third-person perspective, not first-person.")
            if words & self.SECOND_PERSON:
                issues.append(f"{scenario_name}: Step: '{step_text}' - Should use third-person perspective, not second-person.")
        return issues

from .base_rule import BaseRule
import re

class NoStepKeywordInStepTextRule(BaseRule):
    """
    Flags steps that contain step keywords in their text (e.g., 'Given', 'When', 'Then', 'And', 'But').
    """
    KEYWORDS = ['given', 'when', 'then', 'and', 'but']
    def check(self, scenario):
        issues = []
        steps = scenario.get('steps', [])
        for step in steps:
            step_text = step.strip().lower()
            for keyword in self.KEYWORDS:
                # Search for keyword in the step text excluding the leading keyword
                # e.g. skip the initial 'Given ' part by slicing off the first token
                text_tail = step_text.split(' ', 1)[1] if ' ' in step_text else ''
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_tail):
                    issues.append(f"Step contains keyword '{keyword}' in text: {step}")
        return issues

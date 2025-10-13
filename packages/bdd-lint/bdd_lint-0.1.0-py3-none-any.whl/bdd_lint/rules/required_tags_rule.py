from .base_rule import BaseRule

class RequiredTagsRule(BaseRule):
    """
    Flags scenarios missing required tags (not supported in your parser yet).
    """
    def __init__(self, required_tags=None):
        self.required_tags = required_tags or []
    def check(self, scenario):
        # Placeholder: always returns empty
        return []

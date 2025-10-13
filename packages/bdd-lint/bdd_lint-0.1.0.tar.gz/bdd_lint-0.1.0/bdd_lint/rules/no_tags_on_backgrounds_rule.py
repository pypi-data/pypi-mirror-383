from .base_rule import BaseRule

class NoTagsOnBackgroundsRule(BaseRule):
    """
    Flags tags on Background sections (not supported in your parser yet).
    """
    def check(self, scenario):
        # This requires feature-level parsing of Backgrounds and tags
        # Placeholder: always returns empty
        return []

from .base_rule import BaseRule
import re

class TagsFormatRule(BaseRule):
    """
    Flags tags that do not match a required format (not supported in your parser yet).
    """
    def __init__(self, tag_pattern=r'^@[a-z0-9_]+$'):
        self.tag_pattern = tag_pattern
    def check(self, scenario):
        # Placeholder: always returns empty
        return []

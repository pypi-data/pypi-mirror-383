from .base_rule import BaseRule

class NoUnnamedFeaturesRule(BaseRule):
    """
    Flags features without a name.
    """
    def check(self, scenario):
        # This rule should be run at the feature level, not scenario level.
        # For now, we check if scenario name starts with 'Feature:' and is empty.
        issues = []
        feature_name = scenario.get('feature_name', '')
        if not feature_name or feature_name.strip() == 'Feature:':
            issues.append("Feature is unnamed.")
        return issues

from .base_rule import BaseRule

class LowerCaseFeatureNameRule(BaseRule):
    """
    Enforces feature names to be lower case.
    """
    def check(self, scenario):
        issues = []
        feature_name = scenario.get('feature_name', '')
        if feature_name and feature_name != feature_name.lower():
            issues.append(f"Feature name should be lower case: {feature_name}")
        return issues

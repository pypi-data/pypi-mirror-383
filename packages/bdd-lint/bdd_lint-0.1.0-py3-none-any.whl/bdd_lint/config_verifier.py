"""Validate bdd-lint configuration files for expected structure and types."""
from typing import Dict, Any, Tuple


def verify_config(cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify a parsed YAML config for required top-level keys and types.

    Returns (ok, message). Does not raise but returns explanatory message on failure.
    """
    if not isinstance(cfg, dict):
        return False, "Config must be a mapping/object"
    rules = cfg.get('rules', {})
    options = cfg.get('options', {})
    if not isinstance(rules, dict):
        return False, "'rules' must be a mapping of rule names to booleans"
    if not isinstance(options, dict):
        return False, "'options' must be a mapping of rule names to option objects"
    # Ensure rules values are booleans
    for k, v in rules.items():
        if not isinstance(v, bool):
            return False, f"Rule '{k}' must be true/false"
    # Options must be mappings
    for k, v in options.items():
        if not isinstance(v, dict):
            return False, f"Options for '{k}' must be a mapping/object"
    return True, "OK"

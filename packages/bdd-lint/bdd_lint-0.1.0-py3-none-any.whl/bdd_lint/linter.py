import argparse
import importlib
import importlib.util
import json
import os
import sys
from typing import List

from bdd_lint.parser.feature_parser import parse_feature_file
from bdd_lint.config_verifier import verify_config
from bdd_lint.models.issue import Issue


def discover_builtin_rules():
    # Dynamically import everything in the rules package and map class names
    import pkgutil
    import bdd_lint.rules as rules_pkg

    mapping = {}
    pkgpath = rules_pkg.__path__
    for finder, name, ispkg in pkgutil.iter_modules(pkgpath):
        if not name.endswith('_rule') and not ispkg:
            # still import the module to register
            pass
        try:
            mod = importlib.import_module(f"bdd_lint.rules.{name}")
        except Exception:
            continue
        # collect classes ending with Rule
        for attr in dir(mod):
            if attr.endswith('Rule'):
                cls = getattr(mod, attr)
                if callable(cls):
                    mapping[attr] = cls
    return mapping


def load_custom_rules(custom_dir: str):
    mapping = {}
    if not os.path.isdir(custom_dir):
        return mapping
    for fname in os.listdir(custom_dir):
        if fname.endswith('.py'):
            rule_name = fname[:-3]
            fpath = os.path.join(custom_dir, fname)
            spec = importlib.util.spec_from_file_location(rule_name, fpath)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
            except Exception:
                continue
            # Expect custom rule class to match filename (CamelCase)
            class_name = ''.join([part.capitalize() for part in rule_name.split('_')])
            if hasattr(mod, class_name):
                mapping[class_name] = getattr(mod, class_name)
    return mapping


def instantiate_rules(all_rules: dict, config_rules: dict, config_options: dict):
    rules = []
    for rule_name, rule_class in all_rules.items():
        if config_rules.get(rule_name, True):
            opts = config_options.get(rule_name, {})
            try:
                if opts:
                    rules.append((rule_name, rule_class(**opts)))
                else:
                    rules.append((rule_name, rule_class()))
            except Exception:
                # skip rules that fail to construct
                continue
    return rules


def run_rules_on_scenarios(rules, scenarios) -> List[Issue]:
    issues = []
    for scenario in scenarios:
        for rule_name, rule in rules:
            try:
                res = rule.check(scenario) or []
            except Exception as e:
                res = [f"Rule {rule_name} crashed: {e}"]
            for msg in res:
                if isinstance(msg, Issue):
                    issues.append(msg)
                else:
                    issues.append(Issue(rule=rule_name, message=str(msg), scenario=scenario.get('name')))
    return issues


def main(argv=None):
    parser = argparse.ArgumentParser(prog='bdd-lint')
    parser.add_argument('feature_file')
    parser.add_argument('--config', '-c', default='.bdd-lint.yml')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    args = parser.parse_args(argv)

    feature_file = args.feature_file

    # Load scenarios — keep using the fallback parser for now
    scenarios = parse_feature_file(feature_file)

    # Load config
    import yaml
    config = {}
    if os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f) or {}
        except Exception:
            print(f"Unable to load config file: {args.config}")
            sys.exit(2)

    ok, msg = verify_config(config)
    if not ok:
        print(f"Invalid config: {msg}")
        sys.exit(2)

    rule_enable = config.get('rules', {})
    rule_options = config.get('options', {})

    all_rules = discover_builtin_rules()
    # custom rules
    custom_map = load_custom_rules(os.path.join(os.path.dirname(__file__), '..', 'custom_rules'))
    all_rules.update(custom_map)

    rules = instantiate_rules(all_rules, rule_enable, rule_options)

    issues = run_rules_on_scenarios(rules, scenarios)

    if args.json:
        print(json.dumps([i.to_dict() for i in issues], indent=2))
    else:
        for i in issues:
            print(str(i))


if __name__ == '__main__':
    main()
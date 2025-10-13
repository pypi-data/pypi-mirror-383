# bdd-lint
A linter for Behave BDD scenarios to enforce grammar and best practices.

## Features
- All major rules from gherkin-lint
- Custom configuration via `.bdd-lint.yml`
- Enable/disable rules and set options
- Support for custom user-defined rules in `custom_rules/`
- CLI config selection: `bdd-lint <feature-file> [--config <config-file>]`

## Supported Rules
 **GivenPastTenseRule**: Enforces past tense for 'Given' steps.
- **WhenPresentTenseRule**: Enforces present tense for 'When' steps.
- **ThenFutureTenseRule**: Enforces future verbs (should, will, shall) for 'Then' steps.
- **OneWhenThenRule**: Restricts each scenario to exactly one When and one Then step.
- **ThirdPersonRule**: Enforces third-person perspective in steps.
- **TenseConsistencyRule**: Ensures consistent tense usage across Given/When/Then.
- **NoEmptyScenariosRule**: Flags scenarios with no steps.
- **NoUnnamedFeaturesRule**: Flags features without a name.
- **NoUnnamedScenariosRule**: Flags scenarios without a name.
- **NoDuplicateScenariosRule**: Flags duplicate scenario names.
- **NoDuplicateStepRule**: Flags duplicate steps within a scenario.
- **NoScenarioOutlinesWithoutExamplesRule**: Flags scenario outlines missing Examples.
- **NoStepKeywordInStepTextRule**: Flags steps containing step keywords in their text.
- **NoMultilineStepRule**: Flags steps that span multiple lines.
- **NoTagsOnBackgroundsRule**: Flags tags on Background sections.
- **ConsistentStepKeywordOrderRule**: Ensures step keywords appear in the order: Given, When, Then.
- **LowerCaseFeatureNameRule**: Enforces feature names to be lower case.
- **LowerCaseScenarioNameRule**: Enforces scenario names to be lower case.
- **MaxScenariosPerFileRule**: Flags if the number of scenarios in a file exceeds a threshold.
- **MaxStepsPerScenarioRule**: Flags if the number of steps in a scenario exceeds a threshold.
- **RequiredTagsRule**: Flags scenarios missing required tags.
- **TagsFormatRule**: Flags tags that do not match a required format.

## Usage
```bash
bdd-lint path/to/feature_file.feature
bdd-lint path/to/feature_file.feature --config custom_config.yml
# Example: output as JSON
bdd-lint path/to/feature_file.feature --json
```

## Testing
Run the unit test suite with pytest:

```bash
pytest -q
```

The project includes a set of unit tests under `tests/unit/` that exercise the parser, each rule, the NLP helper heuristics and the configuration verifier.

## Configuration
Create a `.bdd-lint.yml` file in your project root:
```yaml
rules:
  GivenPastTenseRule: true
  MaxScenariosPerFileRule: true
options:
  MaxScenariosPerFileRule:
    max_scenarios: 5
```

## Custom Rules
Place your custom rule Python files in the `custom_rules/` directory. Each file should define a class named in CamelCase matching the filename, inheriting from `BaseRule`.

Example: `custom_rules/my_custom_rule.py`
```python
from bdd_lint.rules.base_rule import BaseRule
class MyCustomRule(BaseRule):
    def check(self, scenario):
        # Custom logic
        return []
```

## Requirements
- Python 3.7+
- textblob, spacy, nltk, pytest, pytest-bdd, gherkin-official
- NLTK/TextBlob corpora and spaCy model are auto-downloaded on install

Notes:
- The library ships with a lightweight NLP helper in `bdd_lint.utils.nlp` which falls back to fast heuristics when TextBlob/spaCy are not available. This keeps tests fast and deterministic.
- Use the `bdd_lint.config_verifier.verify_config` helper to validate `.bdd-lint.yml` files programmatically.
- The CLI returns human-readable messages by default or a JSON array of issue objects when `--json` is used. Each issue is represented by the `bdd_lint.models.issue.Issue` dataclass and includes `rule`, `message`, `scenario`, `line`, and `severity` keys.

## License
MIT
from dataclasses import dataclass
from typing import Optional


@dataclass
class Issue:
    rule: str
    message: str
    scenario: Optional[str] = None
    line: Optional[int] = None
    severity: str = "warning"

    def to_dict(self):
        return {
            'rule': self.rule,
            'message': self.message,
            'scenario': self.scenario,
            'line': self.line,
            'severity': self.severity,
        }

    def __str__(self):
        if self.scenario:
            return f"{self.scenario}: {self.message} ({self.rule})"
        return f"{self.message} ({self.rule})"

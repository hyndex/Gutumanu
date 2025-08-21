"""Parser for rule definitions expressed in a small YAML DSL.

The DSL is intentionally tiny and maps directly to Python data structures.
A rule document is expected to look like::

    name: Example rule
    when: "payload['value'] > 10"
    actions:
      - type: log
        message: "Value is high"
    dedupe_key: "value:{payload[id]}"
    escalation: [60, 300]

The parser validates the structure and returns a dictionary representation
that can be consumed by :class:`rules.engine.RuleEngine`.
"""
from __future__ import annotations

from typing import Any, Dict, List

import yaml


class RuleParseError(ValueError):
    """Raised when the YAML document is not a valid rule definition."""


def parse_rules(src: str) -> Dict[str, Any]:
    """Parse a YAML rule definition string.

    Parameters
    ----------
    src: str
        YAML document describing a rule.

    Returns
    -------
    Dict[str, Any]
        Normalised rule definition.
    """
    try:
        data = yaml.safe_load(src) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        raise RuleParseError(str(exc)) from exc

    if not isinstance(data, dict):
        raise RuleParseError("Rule document must be a mapping")

    name = data.get("name") or "rule"
    condition = data.get("when")
    actions = data.get("actions", [])
    dedupe_key = data.get("dedupe_key")
    escalation = data.get("escalation", [])

    if condition is None:
        raise RuleParseError("'when' clause is required")
    if not isinstance(actions, list):
        raise RuleParseError("'actions' must be a list")

    return {
        "name": name,
        "when": condition,
        "actions": actions,
        "dedupe_key": dedupe_key,
        "escalation": escalation,
    }

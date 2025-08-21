"""Rule execution orchestrator."""
from __future__ import annotations

import inspect
from typing import Any, Dict, Iterable, List

from . import db


class RuleEngine:
    """Execute parsed rules against payloads.

    The engine evaluates the ``when`` expression of a rule using ``eval`` with a
    context exposing the ``payload``.  If the condition evaluates to ``True`` the
    associated actions are returned after deduplication checks.
    """

    def __init__(self, rules: Iterable[Dict[str, Any]]):
        self.rules = list(rules)

    def run(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate all rules against ``payload`` and return triggered actions."""
        triggered: List[Dict[str, Any]] = []
        for rule in self.rules:
            name = rule["name"]
            condition = rule["when"]
            try:
                result = bool(eval(condition, {}, {"payload": payload}))
            except Exception:  # pragma: no cover - defensive
                result = False
            if not result:
                continue

            dedupe_key_template = rule.get("dedupe_key") or name
            try:
                dedupe_key = dedupe_key_template.format(payload=payload)
            except Exception:
                dedupe_key = dedupe_key_template
            escalation = [int(e) for e in rule.get("escalation", [])]

            rule_id = db.save_rule(name, "")  # store rule metadata if not present
            should_run = db.log_action(rule_id, dedupe_key, escalation)
            if should_run:
                triggered.extend(rule.get("actions", []))
        return triggered

"""
Grammar validation utilities for SHUGGIE.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Mapping, Sequence, Set, Tuple

from shuggie.grammar import Grammar, Rule

Severity = str  # "error" or "warning"


@dataclass(frozen=True)
class ValidationIssue:
    """Represents a single validation finding."""

    severity: Severity
    message: str
    symbol: str | None = None

    @property
    def is_error(self) -> bool:
        return self.severity == "error"


@dataclass(frozen=True)
class GrammarValidationResult:
    """Collection of validation findings for a grammar."""

    issues: Tuple[ValidationIssue, ...]

    @property
    def has_errors(self) -> bool:
        return any(issue.is_error for issue in self.issues)

    @property
    def errors(self) -> Tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.is_error)

    @property
    def warnings(self) -> Tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if not issue.is_error)

    def summary(self) -> str:
        if not self.issues:
            return "Grammar validation succeeded with no issues."
        parts = []
        for issue in self.issues:
            prefix = "ERROR" if issue.is_error else "WARNING"
            if issue.symbol:
                parts.append(f"{prefix}: {issue.symbol} -> {issue.message}")
            else:
                parts.append(f"{prefix}: {issue.message}")
        return "\n".join(parts)


def validate_grammar(grammar: Grammar) -> GrammarValidationResult:
    """
    Validate grammar structure and weighting, returning any issues discovered.
    """
    issues: List[ValidationIssue] = []

    reachable = _reachable_nonterminals(grammar)
    declared = set(grammar.nonterminals())
    unreachable = declared - reachable
    for symbol in sorted(unreachable):
        issues.append(
            ValidationIssue(
                "warning",
                "Nonterminal is never reached from the start symbol.",
                symbol,
            )
        )

    productive = _productive_nonterminals(grammar)
    for symbol in sorted(declared):
        if symbol not in productive:
            severity: Severity = (
                "error" if symbol == grammar.start_symbol else "warning"
            )
            issues.append(
                ValidationIssue(
                    severity,
                    "Nonterminal cannot derive a string of terminals.",
                    symbol,
                )
            )

    for rule in grammar:
        if len(rule) == 0:
            issues.append(
                ValidationIssue(
                    "error",
                    "Rule has no productions.",
                    rule.symbol,
                )
            )
            continue

        if rule.total_weight <= 0:
            issues.append(
                ValidationIssue(
                    "error",
                    "Rule has non-positive total weight.",
                    rule.symbol,
                )
            )

        for index, production in enumerate(rule.productions):
            if production.weight <= 0:
                issues.append(
                    ValidationIssue(
                        "error",
                        f"Production #{index} has non-positive weight {production.weight}.",
                        rule.symbol,
                    )
                )

    if _has_reachable_productive_cycle(grammar, reachable, productive):
        issues.append(
            ValidationIssue(
                "warning",
                "Grammar contains a productive cycle; maximum derivation depth may be unbounded.",
                None,
            )
        )

    return GrammarValidationResult(tuple(issues))


def _reachable_nonterminals(grammar: Grammar) -> Set[str]:
    reachable: Set[str] = set()
    to_visit: List[str] = [grammar.start_symbol]

    while to_visit:
        symbol = to_visit.pop()
        if symbol in reachable:
            continue
        reachable.add(symbol)

        rule = grammar.get_rule(symbol)
        if not rule:
            continue
        for production in rule:
            for token in production:
                if grammar.is_nonterminal(token) and token not in reachable:
                    to_visit.append(token)

    return reachable


def _productive_nonterminals(grammar: Grammar) -> Set[str]:
    productive: Set[str] = set()
    changed = True
    while changed:
        changed = False
        for rule in grammar:
            if rule.symbol in productive:
                continue
            for production in rule:
                if all(
                    token in productive or not grammar.is_nonterminal(token)
                    for token in production
                ):
                    productive.add(rule.symbol)
                    changed = True
                    break
    return productive


def _has_reachable_productive_cycle(
    grammar: Grammar,
    reachable: Set[str],
    productive: Set[str],
) -> bool:
    graph = {rule.symbol: set() for rule in grammar}
    for rule in grammar:
        for production in rule:
            for token in production:
                if grammar.is_nonterminal(token):
                    graph[rule.symbol].add(token)

    visited: Set[str] = set()
    stack: Set[str] = set()

    def visit(symbol: str) -> bool:
        visited.add(symbol)
        stack.add(symbol)
        for successor in graph.get(symbol, ()):
            if successor not in reachable or successor not in productive:
                continue
            if successor not in visited:
                if visit(successor):
                    return True
            elif successor in stack:
                return True
        stack.remove(symbol)
        return False

    for symbol in reachable:
        if symbol in productive and symbol not in visited:
            if visit(symbol):
                return True
    return False

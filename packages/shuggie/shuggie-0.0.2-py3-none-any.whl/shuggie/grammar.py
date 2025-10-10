"""
Core data structures representing SHUGGIE grammars.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence, Tuple


def _coerce_symbol_sequence(symbols: Sequence[str]) -> Tuple[str, ...]:
    if isinstance(symbols, str):
        raise TypeError("Production symbols must be provided as a sequence of strings.")
    coerced = tuple(str(symbol) for symbol in symbols)
    if not coerced:
        # Empty productions are allowed and represent epsilon.
        return tuple()
    return coerced


@dataclass(frozen=True)
class Production:
    """A single production with an ordered sequence of symbols or literals."""

    symbols: Tuple[str, ...]
    weight: int = 1
    metadata: Mapping[str, Any] | None = None

    def __init__(
        self,
        symbols: Sequence[str],
        weight: int = 1,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if weight < 0:
            raise ValueError("Production weight must be non-negative.")
        object.__setattr__(self, "symbols", _coerce_symbol_sequence(symbols))
        object.__setattr__(self, "weight", int(weight))
        if metadata is None:
            object.__setattr__(self, "metadata", None)
        else:
            object.__setattr__(self, "metadata", MappingProxyType(dict(metadata)))

    def __iter__(self) -> Iterator[str]:
        return iter(self.symbols)

    def with_metadata(self, **metadata: Any) -> "Production":
        """
        Return a new Production with the given metadata merged onto any existing metadata.
        """
        base = dict(self.metadata or {})
        base.update(metadata)
        return Production(self.symbols, self.weight, metadata=base)


@dataclass
class Rule:
    """A grammar rule that maps a nonterminal symbol to multiple productions."""

    symbol: str
    productions: List[Production] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("Rule symbol cannot be empty.")

    def add_production(self, production: Production) -> None:
        self.productions.append(production)

    def extend(self, productions: Iterable[Production]) -> None:
        self.productions.extend(productions)

    @property
    def total_weight(self) -> int:
        return sum(prod.weight for prod in self.productions)

    def __iter__(self) -> Iterator[Production]:
        return iter(self.productions)

    def __len__(self) -> int:
        return len(self.productions)

    def normalized_weights(self) -> List[float]:
        """
        Return the normalized probability for each production in order.

        Raises:
            ValueError: If the total weight is zero or negative.
        """
        total = self.total_weight
        if total <= 0:
            raise ValueError(
                f"Cannot normalize weights for rule {self.symbol!r} with total {total}."
            )
        return [production.weight / total for production in self.productions]


class Grammar:
    """Represents a SHUGGIE grammar with rules and a start symbol."""

    def __init__(self, start_symbol: str, rules: Iterable[Rule] | None = None) -> None:
        if not start_symbol:
            raise ValueError("Start symbol cannot be empty.")
        self.start_symbol = start_symbol
        self._rules: Dict[str, Rule] = {}
        if rules:
            for rule in rules:
                self.add_rule(rule)

    @classmethod
    def from_mapping(
        cls, start_symbol: str, mapping: Mapping[str, Iterable[Production]]
    ) -> "Grammar":
        rules = [
            Rule(symbol, list(productions)) for symbol, productions in mapping.items()
        ]
        return cls(start_symbol=start_symbol, rules=rules)

    def add_rule(self, rule: Rule) -> None:
        if rule.symbol in self._rules:
            existing = self._rules[rule.symbol]
            existing.extend(rule.productions)
        else:
            self._rules[rule.symbol] = rule

    def remove_rule(self, symbol: str) -> None:
        self._rules.pop(symbol, None)

    def upsert_rule(self, symbol: str, productions: Iterable[Production]) -> None:
        rule = self._rules.get(symbol)
        if rule:
            rule.productions = list(productions)
        else:
            self._rules[symbol] = Rule(symbol, list(productions))

    def get_rule(self, symbol: str) -> Rule | None:
        return self._rules.get(symbol)

    def __getitem__(self, symbol: str) -> Rule:
        rule = self.get_rule(symbol)
        if rule is None:
            raise KeyError(symbol)
        return rule

    def rules(self) -> List[Rule]:
        return list(self._rules.values())

    def nonterminals(self) -> List[str]:
        return list(self._rules.keys())

    def terminals(self) -> List[str]:
        nonterminals = set(self._rules.keys())
        terminals: set[str] = set()
        for rule in self._rules.values():
            for production in rule:
                for symbol in production:
                    if symbol not in nonterminals:
                        terminals.add(symbol)
        return sorted(terminals)

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self._rules

    def __contains__(self, symbol: str) -> bool:
        return self.is_nonterminal(symbol)

    def __iter__(self) -> Iterator[Rule]:
        return iter(self._rules.values())

    def __len__(self) -> int:
        return len(self._rules)

    def production_probabilities(self, symbol: str) -> List[Tuple[Production, float]]:
        """
        Return productions for `symbol` paired with their normalized probabilities.

        Raises:
            KeyError: If `symbol` is not present in the grammar.
            ValueError: If the total weight for the rule is zero or negative.
        """
        rule = self[symbol]
        weights = rule.normalized_weights()
        return list(zip(rule.productions, weights))

    def verify(self, *, raise_on_error: bool = False) -> "GrammarValidationResult":
        """
        Validate structural properties of the grammar.

        Args:
            raise_on_error: When True, raise ValueError if validation finds errors.
        """
        from shuggie.validation import validate_grammar

        result = validate_grammar(self)
        if raise_on_error and result.has_errors:
            raise ValueError(result.summary())
        return result

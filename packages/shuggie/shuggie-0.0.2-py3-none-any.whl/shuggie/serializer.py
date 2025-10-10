"""
Parsing and serialization for `.shuggie` grammar files.
"""

from __future__ import annotations

import shlex
from collections import OrderedDict
from typing import Dict, Iterable, List

from shuggie.grammar import Grammar, Production, Rule

COMMENT_PREFIX = "#"


def _strip_inline_comment(line: str) -> str:
    if COMMENT_PREFIX not in line:
        return line
    prefix, _comment = line.split(COMMENT_PREFIX, 1)
    return prefix


class GrammarParser:
    """Parses `.shuggie` formatted text into a Grammar instance."""

    def parse(self, text: str) -> Grammar:
        rules: Dict[str, List[Production]] = OrderedDict()
        start_symbol: str | None = None

        for index, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith(COMMENT_PREFIX):
                continue

            line = _strip_inline_comment(line).strip()
            if not line:
                continue

            symbol, weight, rhs_symbols = self._parse_rule_line(line, index)
            if start_symbol is None:
                start_symbol = symbol

            productions = rules.setdefault(symbol, [])
            productions.append(Production(rhs_symbols, weight))

        if start_symbol is None:
            raise ValueError("No rules found in `.shuggie` text.")

        rule_objs = [Rule(symbol, prods) for symbol, prods in rules.items()]
        return Grammar(start_symbol, rule_objs)

    def _parse_rule_line(self, line: str, index: int) -> tuple[str, int, List[str]]:
        if "," not in line:
            raise ValueError(f"Line {index}: missing ',' separator: {line!r}")
        lhs, remainder = line.split(",", 1)
        symbol = lhs.strip()
        if not symbol:
            raise ValueError(f"Line {index}: symbol cannot be empty.")

        if "=" not in remainder:
            raise ValueError(f"Line {index}: missing '=' separator: {line!r}")
        weight_part, rhs_part = remainder.split("=", 1)
        weight_str = weight_part.strip()
        if not weight_str:
            raise ValueError(f"Line {index}: weight is missing for symbol {symbol!r}.")

        try:
            weight = int(weight_str)
        except ValueError as exc:
            raise ValueError(f"Line {index}: invalid weight {weight_str!r}.") from exc
        if weight < 0:
            raise ValueError(
                f"Line {index}: weight must be non-negative for {symbol!r}."
            )

        rhs_tokens = self._tokenize_rhs(rhs_part)
        return symbol, weight, rhs_tokens

    def _tokenize_rhs(self, rhs_part: str) -> List[str]:
        stripped = rhs_part.strip()
        if not stripped:
            return []
        return shlex.split(stripped)


class GrammarWriter:
    """Serializes a Grammar instance to `.shuggie` formatted text."""

    def write(self, grammar: Grammar) -> str:
        try:
            start_rule = grammar[grammar.start_symbol]
        except KeyError as exc:
            raise ValueError(
                f"Start symbol {grammar.start_symbol!r} has no rule in the grammar."
            ) from exc

        lines: List[str] = []
        lines.extend(self._emit_rule_lines(start_rule))

        for symbol in grammar.nonterminals():
            if symbol == grammar.start_symbol:
                continue
            lines.extend(self._emit_rule_lines(grammar[symbol]))

        return "\n".join(lines)

    def _emit_rule_lines(self, rule: Rule) -> Iterable[str]:
        for production in rule:
            rhs = " ".join(shlex.quote(token) for token in production.symbols)
            line = f"{rule.symbol}, {production.weight} = {rhs}".rstrip()
            yield line

"""
Introspection and analysis helpers for SHUGGIE grammars.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Dict, Iterable, List, Mapping, Set, Tuple

from shuggie.grammar import Grammar, Production


@dataclass(frozen=True)
class GrammarStatistics:
    """Basic counts and aggregates describing a grammar."""

    nonterminal_count: int
    terminal_count: int
    production_count: int
    max_production_length: int
    average_branching_factor: float


@dataclass(frozen=True)
class DepthEstimate:
    """
    Approximates minimal derivation depth and whether expansions are unbounded.
    """

    min_depth: int | None
    is_unbounded: bool
    notes: Tuple[str, ...] = ()


def grammar_statistics(grammar: Grammar) -> GrammarStatistics:
    nonterminal_count = len(grammar)
    terminals = grammar.terminals()
    production_lengths: List[int] = []
    branching: List[int] = []

    for rule in grammar:
        branching.append(len(rule))
        for production in rule:
            production_lengths.append(len(production.symbols))

    production_count = sum(branching)
    max_production_length = max(production_lengths, default=0)
    average_branching = sum(branching) / len(branching) if branching else 0.0

    return GrammarStatistics(
        nonterminal_count=nonterminal_count,
        terminal_count=len(terminals),
        production_count=production_count,
        max_production_length=max_production_length,
        average_branching_factor=average_branching,
    )


def estimate_depth_bounds(
    grammar: Grammar,
    *,
    max_iterations: int = 64,
) -> DepthEstimate:
    """
    Estimate minimal derivation depth from the start symbol and detect unbounded cycles.
    """
    productive = _productive_nonterminals(grammar)
    reachable = _reachable_nonterminals(grammar)
    notes: List[str] = []

    min_depths: Dict[str, float] = {symbol: inf for symbol in grammar.nonterminals()}
    if grammar.start_symbol not in productive:
        notes.append(
            "Start symbol is not productive; derivations may not reach terminals."
        )
        return DepthEstimate(min_depth=None, is_unbounded=False, notes=tuple(notes))

    for iteration in range(max_iterations):
        updated = False
        for rule in grammar:
            best_depth = min_depths[rule.symbol]
            for production in rule:
                depth = _production_depth_estimate(production, min_depths, grammar)
                if depth < best_depth:
                    min_depths[rule.symbol] = depth
                    best_depth = depth
                    updated = True
        if not updated:
            break
    else:
        notes.append(
            "Depth estimation reached iteration limit; values may be approximate."
        )

    min_depth = int(min_depths.get(grammar.start_symbol, inf))
    if min_depth == inf:
        min_depth = None

    unbounded = _has_reachable_productive_cycle(grammar, reachable, productive)
    if unbounded:
        notes.append("Grammar contains a productive cycle; maximum depth is unbounded.")

    return DepthEstimate(
        min_depth=min_depth, is_unbounded=unbounded, notes=tuple(notes)
    )


def grammar_to_dot(
    grammar: Grammar,
    *,
    include_weights: bool = True,
) -> str:
    """
    Emit a Graphviz DOT representation of the grammar structure.
    """
    lines = ["digraph Grammar {", "    rankdir=LR;", '    node [fontname="Helvetica"];']
    terminals = grammar.terminals()
    terminal_nodes = {literal: _terminal_node_id(literal) for literal in terminals}

    emitted_terminals: Set[str] = set()

    for symbol in grammar.nonterminals():
        label = _escape_dot_label(symbol)
        shape = "doublecircle" if symbol == grammar.start_symbol else "ellipse"
        lines.append(f'    "{symbol}" [label="{label}", shape={shape}];')

    for literal, node_id in terminal_nodes.items():
        label = _escape_dot_label(literal)
        lines.append(f'    "{node_id}" [label="{label}", shape=box, style="rounded"];')
        emitted_terminals.add(node_id)

    for rule in grammar:
        for index, production in enumerate(rule.productions):
            prod_node = f"{rule.symbol}__prod__{index}"
            rhs_label = " ".join(production.symbols) if production.symbols else "ε"
            rhs_label = _escape_dot_label(rhs_label)
            lines.append(f'    "{prod_node}" [label="{rhs_label}", shape=plaintext];')
            edge_label = f' [label="{production.weight}"]' if include_weights else ""
            lines.append(f'    "{rule.symbol}" -> "{prod_node}"{edge_label};')
            for token in production.symbols:
                if grammar.is_nonterminal(token):
                    lines.append(f'    "{prod_node}" -> "{token}";')
                else:
                    node_id = terminal_nodes.setdefault(token, _terminal_node_id(token))
                    if node_id not in emitted_terminals:
                        label = _escape_dot_label(token)
                        lines.append(
                            f'    "{node_id}" [label="{label}", shape=box, style="rounded"];'
                        )
                        emitted_terminals.add(node_id)
                    lines.append(f'    "{prod_node}" -> "{node_id}" [style=dashed];')

    lines.append("}")
    return "\n".join(lines)


def _production_depth_estimate(
    production: Production,
    min_depths: Mapping[str, float],
    grammar: Grammar,
) -> float:
    depth = 1.0
    for token in production.symbols:
        if grammar.is_nonterminal(token):
            depth = max(depth, 1.0 + min_depths.get(token, inf))
    return depth


def _terminal_node_id(literal: str) -> str:
    return f"terminal::{literal}"


def _escape_dot_label(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


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

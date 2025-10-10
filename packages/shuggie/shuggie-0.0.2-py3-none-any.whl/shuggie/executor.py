"""
Tools for executing SHUGGIE grammars.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from shuggie.grammar import Grammar, Production, Rule


@dataclass(frozen=True)
class TraceStep:
    """Records which production was chosen for a symbol during execution."""

    symbol: str
    production: Production
    depth: int


@dataclass(frozen=True)
class SampleResult:
    """Encapsulates sampled text alongside its production trace."""

    text: str
    trace: Tuple[TraceStep, ...]


class GrammarExecutor:
    """Provides grammar expansion utilities."""

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def generate_all(
        self,
        limit: int | None = None,
        *,
        max_depth: int = 64,
    ) -> List[str]:
        """
        Generate all possible expansions of the start symbol up to an optional limit.

        The expansions are produced in a deterministic depth-first order. Set `limit`
        to cap the number of results for recursive grammars.
        """
        results: List[str] = []
        self._expand_sequence(
            (self.grammar.start_symbol,),
            [],
            results,
            limit=limit,
            depth=0,
            max_depth=max_depth,
        )
        return results

    def sample(
        self,
        *,
        rng: random.Random | None = None,
        max_depth: int = 64,
        top_k: int | None = None,
        top_p: float | None = None,
        return_trace: bool = False,
    ) -> str | SampleResult:
        """
        Sample a single expansion with optional top-k or nucleus (top-p) filtering.

        Provide a `random.Random` instance via `rng` for reproducibility.
        """
        if rng is None:
            rng = random.Random()
        trace: List[TraceStep] = []
        tokens = self._sample_sequence(
            (self.grammar.start_symbol,),
            rng=rng,
            depth=0,
            max_depth=max_depth,
            top_k=top_k,
            top_p=top_p,
            trace=trace,
        )
        text = " ".join(tokens).strip()
        if return_trace:
            return SampleResult(text=text, trace=tuple(trace))
        return text

    def trace_sample(
        self,
        *,
        rng: random.Random | None = None,
        max_depth: int = 64,
        top_k: int | None = None,
        top_p: float | None = None,
    ) -> SampleResult:
        """
        Convenience wrapper around `sample` that always returns a `SampleResult`.
        """
        result = self.sample(
            rng=rng,
            max_depth=max_depth,
            top_k=top_k,
            top_p=top_p,
            return_trace=True,
        )
        assert isinstance(result, SampleResult)
        return result

    def sample_best(
        self,
        *,
        max_depth: int = 64,
        return_trace: bool = False,
    ) -> str | SampleResult:
        """
        Deterministically choose the highest-weight production at each step.
        """
        trace: List[TraceStep] = []
        tokens = self._best_sequence(
            (self.grammar.start_symbol,),
            depth=0,
            max_depth=max_depth,
            trace=trace,
        )
        text = " ".join(tokens).strip()
        if return_trace:
            return SampleResult(text=text, trace=tuple(trace))
        return text

    def generate_best(self, *, max_depth: int = 64) -> str:
        """
        Generate the highest-weight deterministic expansion.
        """
        result = self.sample_best(max_depth=max_depth, return_trace=False)
        assert isinstance(result, str)
        return result

    def _expand_sequence(
        self,
        sequence: Sequence[str],
        prefix: List[str],
        results: List[str],
        *,
        limit: int | None,
        depth: int,
        max_depth: int,
    ) -> None:
        if limit is not None and len(results) >= limit:
            return
        if not sequence:
            results.append(" ".join(prefix).strip())
            return
        if depth > max_depth:
            raise RecursionError(
                f"Maximum expansion depth {max_depth} exceeded; grammar may be recursive."
            )

        head, *tail = sequence
        if self.grammar.is_nonterminal(head):
            rule = self.grammar[head]
            if not rule.productions:
                raise ValueError(f"No productions available for symbol {head!r}.")
            next_depth = depth + 1
            for production in rule:
                combined_sequence = production.symbols + tuple(tail)
                self._expand_sequence(
                    combined_sequence,
                    prefix,
                    results,
                    limit=limit,
                    depth=next_depth,
                    max_depth=max_depth,
                )
        else:
            extended_prefix = prefix + [head]
            self._expand_sequence(
                tail,
                extended_prefix,
                results,
                limit=limit,
                depth=depth,
                max_depth=max_depth,
            )

    def _sample_sequence(
        self,
        sequence: Sequence[str],
        *,
        rng: random.Random,
        depth: int,
        max_depth: int,
        top_k: int | None,
        top_p: float | None,
        trace: List[TraceStep],
    ) -> List[str]:
        if not sequence:
            return []
        if depth > max_depth:
            raise RecursionError(
                f"Maximum sampling depth {max_depth} exceeded; grammar may be recursive."
            )

        head, *tail = sequence
        if self.grammar.is_nonterminal(head):
            rule = self.grammar[head]
            production = self._weighted_choice(rule, rng, top_k=top_k, top_p=top_p)
            trace.append(TraceStep(symbol=head, production=production, depth=depth))
            combined_sequence = production.symbols + tuple(tail)
            return self._sample_sequence(
                combined_sequence,
                rng=rng,
                depth=depth + 1,
                max_depth=max_depth,
                top_k=top_k,
                top_p=top_p,
                trace=trace,
            )

        return [head] + self._sample_sequence(
            tail,
            rng=rng,
            depth=depth,
            max_depth=max_depth,
            top_k=top_k,
            top_p=top_p,
            trace=trace,
        )

    def _best_sequence(
        self,
        sequence: Sequence[str],
        *,
        depth: int,
        max_depth: int,
        trace: List[TraceStep],
    ) -> List[str]:
        if not sequence:
            return []
        if depth > max_depth:
            raise RecursionError(
                f"Maximum expansion depth {max_depth} exceeded while selecting best sequence."
            )

        head, *tail = sequence
        if self.grammar.is_nonterminal(head):
            rule = self.grammar[head]
            if not rule.productions:
                raise ValueError(f"No productions available for symbol {head!r}.")
            production = max(
                rule.productions,
                key=lambda prod: (prod.weight, -len(prod.symbols)),
            )
            trace.append(TraceStep(symbol=head, production=production, depth=depth))
            combined_sequence = production.symbols + tuple(tail)
            return self._best_sequence(
                combined_sequence,
                depth=depth + 1,
                max_depth=max_depth,
                trace=trace,
            )

        return [head] + self._best_sequence(
            tail,
            depth=depth,
            max_depth=max_depth,
            trace=trace,
        )

    def _weighted_choice(
        self,
        rule: Rule,
        rng: random.Random,
        *,
        top_k: int | None,
        top_p: float | None,
    ) -> Production:
        candidates = self._candidate_productions(rule, top_k=top_k, top_p=top_p)
        total_weight = sum(prod.weight for prod in candidates)
        if total_weight <= 0:
            raise ValueError(
                f"Rule {rule.symbol!r} has no positive-weight productions."
            )

        choice_point = rng.random() * total_weight
        cumulative = 0
        for production in candidates:
            cumulative += production.weight
            if choice_point < cumulative:
                return production
        # Due to floating point rounding, return the last production as a fallback.
        return candidates[-1]

    def _candidate_productions(
        self,
        rule: Rule,
        *,
        top_k: int | None,
        top_p: float | None,
    ) -> List[Production]:
        if not rule.productions:
            raise ValueError(f"No productions available for symbol {rule.symbol!r}.")

        candidates = list(rule.productions)
        if top_k is None and top_p is None:
            return candidates

        order_map = {id(prod): index for index, prod in enumerate(rule.productions)}
        sorted_prods = sorted(
            candidates,
            key=lambda prod: (-prod.weight, order_map[id(prod)]),
        )

        if top_k is not None:
            if top_k <= 0:
                raise ValueError("top_k must be positive when provided.")
            sorted_prods = sorted_prods[: min(top_k, len(sorted_prods))]

        if top_p is not None:
            if not 0 < top_p <= 1:
                raise ValueError("top_p must be in the interval (0, 1].")
            total_weight = sum(prod.weight for prod in sorted_prods)
            if total_weight <= 0:
                raise ValueError(
                    f"Rule {rule.symbol!r} has no positive-weight productions."
                )
            cumulative = 0.0
            nucleus: List[Production] = []
            for production in sorted_prods:
                normalized = production.weight / total_weight
                cumulative += normalized
                nucleus.append(production)
                if cumulative >= top_p:
                    break
            sorted_prods = nucleus

        # Preserve the rule's original order when returning to keep deterministic behaviour.
        return sorted(sorted_prods, key=lambda prod: order_map[id(prod)])

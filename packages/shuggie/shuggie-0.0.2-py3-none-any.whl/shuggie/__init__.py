"""
SHUGGIE: Standard Human Understandable Generative Grammar Interpreter and Executor.
"""

from .analysis import (
    DepthEstimate,
    GrammarStatistics,
    estimate_depth_bounds,
    grammar_statistics,
    grammar_to_dot,
)
from .executor import GrammarExecutor, SampleResult, TraceStep
from .grammar import Grammar, Production, Rule
from .io import dump_shuggie, load_shuggie
from .serializer import GrammarParser, GrammarWriter
from .validation import GrammarValidationResult, ValidationIssue, validate_grammar

__version__ = "0.0.2"

__all__ = [
    "Grammar",
    "Rule",
    "Production",
    "GrammarExecutor",
    "SampleResult",
    "TraceStep",
    "GrammarParser",
    "GrammarWriter",
    "GrammarValidationResult",
    "ValidationIssue",
    "validate_grammar",
    "GrammarStatistics",
    "DepthEstimate",
    "grammar_statistics",
    "estimate_depth_bounds",
    "grammar_to_dot",
    "load_shuggie",
    "dump_shuggie",
    "__version__",
]

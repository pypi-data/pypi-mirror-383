"""
File I/O helpers for SHUGGIE grammars.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Union

from shuggie.grammar import Grammar
from shuggie.serializer import GrammarParser, GrammarWriter

PathLike = Union[str, Path]


def load_shuggie(path: PathLike, *, encoding: str = "utf-8") -> Grammar:
    """
    Load a `.shuggie` grammar from the given file path.
    """
    file_path = Path(path)
    text = file_path.read_text(encoding=encoding)
    parser = GrammarParser()
    return parser.parse(text)


def dump_shuggie(
    grammar: Grammar,
    path: PathLike,
    *,
    encoding: str = "utf-8",
) -> None:
    """
    Write the grammar to `path` in `.shuggie` format.
    """
    file_path = Path(path)
    writer = GrammarWriter()
    text = writer.write(grammar)
    file_path.write_text(text, encoding=encoding)

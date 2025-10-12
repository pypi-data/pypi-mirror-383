from __future__ import annotations

from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, slots=True)
class Namespace(Identifier):
    """Namespace value object (inherits Identifier validation)."""

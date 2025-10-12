from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .id import EntityId
    from .namespace import Namespace


@dataclass(frozen=True, slots=True)
class Obj:
    """Object value with namespace and id."""

    namespace: Namespace
    id: EntityId

    def __str__(self) -> str:
        return f"{self.namespace}:{self.id}"

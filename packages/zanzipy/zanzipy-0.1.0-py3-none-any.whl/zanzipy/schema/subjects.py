from dataclasses import dataclass

from ..models.namespace import Namespace
from ..models.relation import Relation as Rel


@dataclass(frozen=True, slots=True)
class SubjectReference:
    """Represents an allowed subject type for a relation.

    Forms supported (SpiceDB compatible):
    - "ns" (e.g., user)
    - "ns#rel" (e.g., group#member)
    - "ns:*" (namespace wildcard)
    """

    namespace: Namespace
    relation: Rel | None = None
    wildcard: bool = False

    def __post_init__(self) -> None:
        # Validate invariant combinations
        if self.wildcard and self.relation is not None:
            raise ValueError("wildcard and relation are mutually exclusive")

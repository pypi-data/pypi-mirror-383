from dataclasses import dataclass

from ..models.relation import Relation as Rel
from .rules import RewriteRule


@dataclass(frozen=True, slots=True)
class PermissionDef:
    """Defines a computed permission: rewrite expression only."""

    name: str
    rewrite: RewriteRule
    description: str | None = None

    def __post_init__(self) -> None:
        # Validate permission name as a relation identifier
        Rel(self.name)

    def to_dict(self) -> dict:
        return {
            "type": "permission",
            "name": self.name,
            "rewrite": self.rewrite.to_dict(),
            "description": self.description,
        }

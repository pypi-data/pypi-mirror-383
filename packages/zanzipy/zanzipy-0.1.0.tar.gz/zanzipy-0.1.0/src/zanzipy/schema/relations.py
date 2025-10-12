from collections.abc import Iterable
from dataclasses import dataclass

from ..models.relation import Relation as Rel
from .rules import RewriteRule
from .subjects import SubjectReference


@dataclass(frozen=True, slots=True)
class RelationDef:
    """Defines a relation: allowed subject types and optional rewrite.

    Note: Relations must declare at least one allowed subject.
    """

    name: str
    allowed_subjects: tuple[SubjectReference, ...]
    rewrite: RewriteRule | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        # Validate relation name
        Rel(self.name)
        if not self.allowed_subjects:
            raise ValueError("Relation must declare at least one allowed subject type")

    @classmethod
    def with_subjects(
        cls,
        name: str,
        subjects: Iterable[SubjectReference],
        rewrite: RewriteRule | None = None,
        description: str | None = None,
    ) -> "RelationDef":
        return cls(
            name=name,
            allowed_subjects=tuple(subjects),
            rewrite=rewrite,
            description=description,
        )

    def to_dict(self) -> dict:
        return {
            "type": "relation",
            "name": self.name,
            "allowed_subjects": [
                {
                    "namespace": s.namespace.value,
                    "relation": (s.relation.value if s.relation else None),
                    "wildcard": s.wildcard,
                }
                for s in self.allowed_subjects
            ],
            "rewrite": self.rewrite.to_dict() if self.rewrite else None,
            "description": self.description,
        }

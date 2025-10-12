from dataclasses import dataclass
import re
from typing import ClassVar, Self

from .errors import InvalidTupleFormatError
from .id import EntityId
from .namespace import Namespace
from .object import Obj
from .relation import Relation
from .subject import Subject


@dataclass(frozen=True, slots=True)
class RelationTuple:
    """
    Represents a Zanzibar relationship tuple.

    Format:
        `object_namespace:object_id#relation@subject_namespace:subject_id[#subject_relation]`

    Constraints:
        - Namespaces and relations must be valid identifiers (alphanumeric, underscore,
          or hyphen, starting with letter or underscore)
        - IDs may contain any characters except `#`, `@`, `:`, and whitespace
        - subject_relation follows the same rules as relation
        - No component may be empty

    Examples:
        - `document:readme#owner@user:alice`
        - `folder:docs#viewer@group:eng#member`
        - `doc:uuid-123-abc#can_read@user:bob`

    Attributes:
        object: The object being related (contains namespace and id)
        relation: The relation name (e.g., 'owner', 'viewer', 'can_read')
        subject: The subject entity (contains namespace, id, and optional
            relation for subject sets)

    Note:
        Instances are immutable and hashable, suitable for use in sets and as dict keys.
    """

    # Complete tuple parsing pattern
    _TUPLE_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"^(?P<object_namespace>[a-zA-Z_][a-zA-Z0-9_-]*)"  # object namespace
        r":(?P<object_id>[^#@:\s]+)"  # object id
        r"#(?P<relation>[a-zA-Z_][a-zA-Z0-9_-]*)"  # relation
        r"@(?P<subject_namespace>[a-zA-Z_][a-zA-Z0-9_-]*)"  # subject namespace
        r":(?P<subject_id>[^#@:\s]+)"  # subject id
        r"(?:#(?P<subject_relation>[a-zA-Z_][a-zA-Z0-9_-]*))?$"  # optional subject rel
    )

    object: Obj
    relation: Relation
    subject: Subject

    @classmethod
    def from_string(cls, tuple_string: str) -> "RelationTuple":
        """Parse a Zanzibar relation tuple string.

        Args:
            tuple_string:
                String in format
                `object_namespace:object_id#relation@subject_namespace:subject_id[#subject_relation]`

        Returns:
            RelationTuple instance

        Raises:
            InvalidTupleFormatError: If the string doesn't match the expected format

        Examples:
            >>> RelationTuple.from_string("document:readme#owner@user:alice")
            >>> RelationTuple.from_string("folder:docs#viewer@group:eng#member")
        """
        match = cls._TUPLE_PATTERN.match(tuple_string)
        if not match:
            raise InvalidTupleFormatError(
                f"Invalid tuple format: '{tuple_string}'. "
                "Expected: 'object_namespace:object_id#relation@subject_namespace:"
                "subject_id[#subject_relation]'. "
                "Namespaces and relations must be valid identifiers "
                "(letters/digits/_/-, start with letter/_). "
                "IDs may contain any characters except '#', '@', ':', and whitespace. "
                "No component may be empty."
            )

        groups = match.groupdict()
        subject_relation = groups["subject_relation"]
        return cls(
            object=Obj(
                Namespace(groups["object_namespace"]),
                EntityId(groups["object_id"]),
            ),
            relation=Relation(groups["relation"]),
            subject=Subject(
                Namespace(groups["subject_namespace"]),
                EntityId(groups["subject_id"]),
                Relation(subject_relation) if subject_relation is not None else None,
            ),
        )

    def to_dict(self) -> dict:
        """Return a dictionary representation of the tuple.

        Returns:
            dict: Dictionary representation of the tuple

        Examples:
            ```python
            >>> RelationTuple.from_string("document:readme#owner@user:alice").to_dict()
            {
                'object_namespace': 'document',
                'object_id': 'readme',
                'relation': 'owner',
                'subject_namespace': 'user',
                'subject_id': 'alice',
                'subject_relation': None
            }
            ```
        """
        return {
            "object_namespace": str(self.object.namespace),
            "object_id": str(self.object.id),
            "relation": str(self.relation),
            "subject_namespace": str(self.subject.namespace),
            "subject_id": str(self.subject.id),
            "subject_relation": (
                str(self.subject.relation)
                if self.subject.relation is not None
                else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a RelationTuple from a dictionary.

        Args:
            data: Dictionary representation of the tuple

        Returns:
            RelationTuple: RelationTuple instance

        Examples:
            ```python
            >>> RelationTuple.from_dict({
            ...     "object_namespace": "document",
            ...     "object_id": "readme",
            ...     "relation": "owner",
            ...     "subject_namespace": "user",
            ...     "subject_id": "alice",
            ... })
            RelationTuple(
                object_namespace='document',
                object_id='readme',
                relation='owner',
                subject_namespace='user',
                subject_id='alice',
                subject_relation=None
            )
            ```
        """
        # Treat presence of key with empty string as invalid
        if "subject_relation" in data and data["subject_relation"] == "":
            # This will raise IdentifierValidationError
            subject_rel = Relation("")
        else:
            subject_rel = (
                Relation(data["subject_relation"])
                if data.get("subject_relation")
                else None
            )
        return cls(
            object=Obj(
                Namespace(data["object_namespace"]),
                EntityId(data["object_id"]),
            ),
            relation=Relation(data["relation"]),
            subject=Subject(
                Namespace(data["subject_namespace"]),
                EntityId(data["subject_id"]),
                subject_rel,
            ),
        )

    def __str__(self) -> str:
        """Return canonical string representation of the tuple."""
        object_str = str(self.object)
        subject_str = str(self.subject)
        return f"{object_str}#{self.relation}@{subject_str}"

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        subject_relation_repr = (
            str(self.subject.relation) if self.subject.relation is not None else None
        )
        return (
            f"RelationTuple("
            f"object_namespace={str(self.object.namespace)!r}, "
            f"object_id={str(self.object.id)!r}, "
            f"relation={str(self.relation)!r}, "
            f"subject_namespace={str(self.subject.namespace)!r}, "
            f"subject_id={str(self.subject.id)!r}, "
            f"subject_relation={subject_relation_repr!r})"
        )

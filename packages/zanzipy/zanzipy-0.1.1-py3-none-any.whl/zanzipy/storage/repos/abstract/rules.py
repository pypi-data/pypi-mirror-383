"""Abstract repository for namespace-scoped rewrite rule definitions.

This repository manages schema definitions that pair a namespace and name with a
rewrite expression (see ``zanzipy.schema.rules.RewriteRule``). It is agnostic to
the concrete entity shape stored by backends; implementations decide whether the
stored entity represents relations, permissions, or a unified definition type.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Iterable

    from zanzipy.schema.rules import RewriteRule


class RulesRepository[TRuleEntity, TKey, TFilter](
    BaseRepository[TRuleEntity, TKey, TFilter], ABC
):
    """Abstract storage interface for rewrite rule definitions.

    Type parameters:
    - ``TRuleEntity``: stored entity representing a definition record
    - ``TKey``: storage key (commonly a tuple of ``(namespace, name)``)
    - ``TFilter``: filter type used to query definitions

    Implementations must define how to construct keys and filters from parts.
    """

    @abstractmethod
    def key_from_parts(self, namespace: str, name: str) -> TKey:
        """Build a key from namespace and name."""

    @abstractmethod
    def make_filter(
        self,
        *,
        namespace: str | None = None,
        name: str | None = None,
    ) -> TFilter:
        """Create a filter for listing/querying definitions."""

    def get_by_name(self, namespace: str, name: str) -> TRuleEntity | None:
        """Fetch a rule definition by ``(namespace, name)`` if present."""

        return self.get(self.key_from_parts(namespace, name))

    def exists_by_name(self, namespace: str, name: str) -> bool:
        """Check existence for ``(namespace, name)`` without fetching body."""

        return self.exists(self.key_from_parts(namespace, name))

    def list_namespace(self, namespace: str) -> Iterable[TRuleEntity]:
        """Iterate all definitions within a namespace."""

        return self.find(self.make_filter(namespace=namespace))

    def find_by_name(self, name: str) -> Iterable[TRuleEntity]:
        """Iterate all definitions across namespaces matching ``name``."""

        return self.find(self.make_filter(name=name))

    def validate_rewrite(self, rewrite: RewriteRule) -> None:
        """Optional hook for implementations to validate rewrite DAGs.

        The base class provides no-op validation. Backends can override to
        enforce limits (depth, width), or pre-validate referenced relation names
        if they have access to the surrounding schema context.
        """

        return None

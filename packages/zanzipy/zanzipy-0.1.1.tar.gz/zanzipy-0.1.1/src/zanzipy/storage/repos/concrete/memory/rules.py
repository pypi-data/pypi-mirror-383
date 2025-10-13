from dataclasses import dataclass
from typing import TYPE_CHECKING

from zanzipy.storage.repos.abstract.rules import RulesRepository

if TYPE_CHECKING:
    from collections.abc import Iterable

    from zanzipy.schema.rules import RewriteRule


@dataclass(frozen=True, slots=True)
class RuleRecord:
    """Simple in-memory record for a rewrite rule definition."""

    namespace: str
    name: str
    rewrite: RewriteRule
    description: str | None = None

    def key(self) -> tuple[str, str]:
        return (self.namespace, self.name)


@dataclass(frozen=True, slots=True)
class RuleFilter:
    """Filter for in-memory rule queries."""

    namespace: str | None = None
    name: str | None = None


class InMemoryRulesRepository(RulesRepository[RuleRecord, tuple[str, str], RuleFilter]):
    """In-memory implementation of RulesRepository.

    Not thread-safe; intended for tests and local prototypes.
    """

    def __init__(self) -> None:
        self._data: dict[tuple[str, str], RuleRecord] = {}

    def key_of(self, entity: RuleRecord) -> tuple[str, str]:
        return entity.key()

    def upsert(self, entity: RuleRecord) -> None:
        self._data[entity.key()] = entity

    def delete_by_key(self, key: tuple[str, str]) -> bool:
        return self._data.pop(key, None) is not None

    def get(self, key: tuple[str, str]) -> RuleRecord | None:
        return self._data.get(key)

    def find(self, filter: RuleFilter) -> Iterable[RuleRecord]:
        ns = filter.namespace
        nm = filter.name
        for record in self._data.values():
            if ns is not None and record.namespace != ns:
                continue
            if nm is not None and record.name != nm:
                continue
            yield record

    def key_from_parts(self, namespace: str, name: str) -> tuple[str, str]:
        return (namespace, name)

    def make_filter(
        self, *, namespace: str | None = None, name: str | None = None
    ) -> RuleFilter:
        return RuleFilter(namespace=namespace, name=name)

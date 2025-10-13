## zanzipy

Pythonic, minimal implementation of Zanzibar-style authorization (ReBAC) for real-world SaaS apps — not Google scale, but practical and solid. Bring your own persistence; everything else to model, write, and check permissions is here.

### Why zanzipy? ✨
- **No extra services**: embed in your app. Implement a tiny repo interface to use any storage (SQL/NoSQL/in-memory).
- **Zanzibar concepts**: relations, permissions, unions/intersections/exclusions, tuple-to-userset (cross-namespace following).
- **Schema-first**: validate rewrites and subject types at registration time.
- **Batteries-included engine**: correctness-first checks and object listing with rule evaluation.

### Project status 🚧
- Early and evolving. Core primitives are implemented and tested, but the API may change.
- Good fit if you want to bootstrap an ACL/Authorization/ReBAC system in Python without running a separate auth service.

### Install
```bash
pip install zanzipy
```

### Quick start (tiny example)
```python
from zanzipy.client import ZanzibarClient
from zanzipy.models import Relation
from zanzipy.schema import (
    NamespaceDef,
    RelationDef,
    PermissionDef,
    SubjectReference,
    ComputedUsersetRule,
    UnionRule,
    SchemaRegistry,
)
from zanzipy.storage.repos import InMemoryRelationRepository

# Define a minimal schema: users and documents
user_ns = NamespaceDef(name="user")
doc_ns = NamespaceDef(
    name="document",
    relations=(
        RelationDef(
            name="owner",
            allowed_subjects=SubjectReference(namespace="user"),
        ),
        RelationDef(
            name="viewer",
            allowed_subjects=SubjectReference(namespace="user"),
        ),
    ),
    permissions=(
        PermissionDef(
            name="can_view",
            rewrite=UnionRule(children=(
                ComputedUsersetRule("owner"),
                ComputedUsersetRule("viewer"),
            )),
        ),
    ),
)

registry = SchemaRegistry()
registry.register_many((user_ns, doc_ns))

client = ZanzibarClient(
    schema=registry,
    relations_repository=InMemoryRelationRepository(),
)

# Write some tuples
client.write("document:readme", "owner", "user:alice")
client.write("document:readme", "viewer", "user:bob")

# Check
assert client.check("document:readme", "can_view", "user:alice") is True
assert client.check("document:readme", "can_view", "user:bob") is True
assert client.check("document:readme", "can_view", "user:eve") is False
```

For a more complete, fun-but-enterprise example (folders, documents, groups, tuple-to-userset), see `examples/boobledrive.py`.

### How it works (at a glance)
- Define namespaces with `RelationDef` and `PermissionDef` using rewrite rules.
- Register them in `SchemaRegistry` (validated on registration).
- Store relation tuples via the client (your storage backend implements the repo interface).
- Evaluate checks using the rules-aware engine (with cycle detection and depth limits).

### Roadmap / TODOs
- [ ] Caching layer (read-through and check-result memoization) ⚡
- [ ] Storage backends (example Postgres/SQLite adapters)
- [ ] More examples (nested folders, exclusion/intersection patterns)
- [ ] Packaging and versioned releases (PyPI)
- [ ] Developer docs (schema patterns, migration tips)
- [ ] Benchmarks and profiling harness
- [x] In-memory repositories for relations and rules
- [x] Core rewrite rules (union, intersection, exclusion, tuple-to-userset)
- [x] Registry validation of schemas

### Bring your own persistence 🧱
You don’t run a server for zanzipy. Implement the lightweight repository interfaces and you’re done:
- `RelationRepository`: store/read relation tuples.
- `RulesRepository` (optional): provide rewrites at runtime; schema remains the source of truth if omitted.

See the in-memory implementations under `src/zanzipy/storage/repos/concrete/memory` as a reference.

### License
Apache-2.0
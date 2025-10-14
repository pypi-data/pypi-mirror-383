### Changed

- Unified `get_triples_to_add` and `get_triples_to_delete` into a single
generic `get_graph_diff` query.
- Updated corresponding tests to use the new generic method.
- Updated `NeatInstanceStore` method to use the new generic query.
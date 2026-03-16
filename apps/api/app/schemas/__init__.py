"""Schema package entrypoint.

This module intentionally avoids eager imports so that V2 schemas can be used
without pulling in legacy model-dependent schema modules during the migration.
"""

__all__: list[str] = []

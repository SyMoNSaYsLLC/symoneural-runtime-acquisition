"""Application definitions. Each module registers ONE application with the
generic registry. Import this package to load every shipped definition; a new
demo is a new module here plus its first-party page content - nothing else."""
from . import dispatchos  # noqa: F401  (registers on import)

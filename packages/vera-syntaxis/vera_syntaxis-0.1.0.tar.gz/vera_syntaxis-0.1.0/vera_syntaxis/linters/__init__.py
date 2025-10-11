"""Architectural linters for Vera Syntaxis."""

# Import all linters in this directory so they are registered.
from . import tight_coupling  # noqa: F401
from . import mvbc  # noqa: F401
from . import circular_dependency  # noqa: F401
from . import god_object  # noqa: F401
from . import feature_envy  # noqa: F401
from . import data_clump  # noqa: F401

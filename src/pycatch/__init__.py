"""pycatch : gestion d'erreurs fluide pour Python, inspirée de Rust."""

from pycatch.core import Err, Ok, Result, UnwrapError
from pycatch.decorators import catch

__version__ = "1.0.0rc1"

__all__ = ["Err", "Ok", "Result", "UnwrapError", "__version__", "catch"]

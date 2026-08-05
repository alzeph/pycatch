"""Result, Ok et Err : gestion d'erreurs explicite façon Rust.

`Result[T, E]` représente soit un succès (`Ok[T]`), soit un échec (`Err[E]`).
Les deux variantes exposent la même API (map, and_then, unwrap, ...) et sont
compatibles avec le pattern matching (`match res: case Ok(val): ...`).

`Ok` et `Err` sont de simples constructeurs, librement instanciables — comme
en Rust, il n'y a pas de factory imposée : `Ok(42)`, `Err(ValueError(...))`.

Chaque responsabilité vit dans son propre module :
- `errors` : `UnwrapError`
- `ok` : la variante succès
- `err` : la variante échec
- `result` : le type `Result[T, E]`
"""

from .err import Err
from .errors import UnwrapError
from .ok import Ok
from .result import Result

__all__ = ["Err", "Ok", "Result", "UnwrapError"]

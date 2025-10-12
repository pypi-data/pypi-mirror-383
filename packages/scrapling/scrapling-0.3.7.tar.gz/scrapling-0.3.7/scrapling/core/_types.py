"""
Type definitions for type checking purposes.
"""

from typing import (
    TYPE_CHECKING,
    cast,
    overload,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Set,
    Literal,
    Optional,
    Pattern,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    Match,
    Mapping,
    Awaitable,
    Protocol,
    Coroutine,
    SupportsIndex,
)

SUPPORTED_HTTP_METHODS = Literal["GET", "POST", "PUT", "DELETE"]
SelectorWaitStates = Literal["attached", "detached", "hidden", "visible"]
PageLoadStates = Literal["commit", "domcontentloaded", "load", "networkidle"]
extraction_types = Literal["text", "html", "markdown"]
StrOrBytes = Union[str, bytes]


try:
    # Python 3.11+
    from typing import Self  # novermin
except ImportError:  # pragma: no cover
    try:
        from typing_extensions import Self  # Backport
    except ImportError:
        Self = object

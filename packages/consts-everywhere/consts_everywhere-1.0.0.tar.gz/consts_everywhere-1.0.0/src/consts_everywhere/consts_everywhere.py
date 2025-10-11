import typing
import typeguard
from . import wrapt


class Const(wrapt.AutoObjectProxy, typing.Generic[typing.TypeVar("T")]):
    def __init__(self, wrapped):
        wrapt.AutoObjectProxy.__init__(self, wrapped)
        
    def _assign_(self, value, *annotation):
        raise TypeError("unsupported  operator (=) for Const object")

    def __iadd__(self, other):
        raise TypeError("unsupported  operator (+=) for Const object")

    def __isub__(self, other):
        raise TypeError("unsupported  operator (-=) for Const object")

    def __imul__(self, other):
        raise TypeError("unsupported  operator (*=) for Const object")

    def __itruediv__(self, other):
        raise TypeError("unsupported  operator (/=) for Const object")

    def __ifloordiv__(self, other):
        raise TypeError("unsupported  operator (//=) for Const object")

    def __imod__(self, other):
        raise TypeError("unsupported  operator (%=) for Const object")

    def __ipow__(self, other):
        raise TypeError("unsupported  operator (**=) for Const object")

    def __ilshift__(self, other):
        raise TypeError("unsupported  operator (<<=) for Const object")

    def __irshift__(self, other):
        raise TypeError("unsupported  operator (>>=) for Const object")

    def __iand__(self, other):
        raise TypeError("unsupported  operator (&=) for Const object")

    def __ixor__(self, other):
        raise TypeError("unsupported  operator (^=) for Const object")

    def __ior__(self, other):
        raise TypeError("unsupported  operator (|=) for Const object")

    def __imatmul__(self, other):
        raise TypeError("unsupported  operator (@=) for Const object")


def check_const_value(value, origin_type, args, memo):
    if type(value).__name__ != "Const":
        raise typeguard.TypeCheckError("is not a Const instance")
    if not args:
        return
    inner_type = args[0]
    try:
        typeguard.check_type_internal(value.__wrapped__, inner_type, memo)
    except typeguard.TypeCheckError:
        raise typeguard.TypeCheckError(f"doesn't wrap an instance of {inner_type}")


def const_lookup(origin_type, args, extras):
    if origin_type is Const:
        return check_const_value
    return None


typeguard.checker_lookup_functions.append(const_lookup)
typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS

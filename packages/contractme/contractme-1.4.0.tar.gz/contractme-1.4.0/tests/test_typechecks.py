from typing import Annotated
from annotated_types import Ge, Lt, Gt
from inspect import get_annotations
import dataclasses
from contractme.typecheck import (
    get_recursive_composite_type_info,
    get_first_structure_error,
    get_constraints_errors,
    ChildMod,
)


type TR2 = TR  # type: ignore
type TR = TR2
type T0 = Annotated[TR, 3]
type T = Annotated[T0, 2]
type T2 = tuple[int, T]
type T3 = Annotated[T2, 1]


def f[TT: T3](a: TT) -> TT:  # pragma: no cover
    return a


def g(a: tuple[int, ...]):  # pragma: no cover
    pass


def h(a: int | Annotated[float, Ge(0.0)]):  # pragma: no cover
    pass


def test_get_info_complex():
    an = get_annotations(f)["a"]
    type_infos = [dataclasses.astuple(e) for e in get_recursive_composite_type_info(an)]
    assert type_infos == [
        (tuple, [1], ChildMod.NONE, (int, T)),
        (int, [], ChildMod.NONE, tuple()),
        (TR, [2, 3], ChildMod.NONE, tuple()),
    ]


def test_get_info_tuple_ellipsis():
    an = get_annotations(g)["a"]
    type_infos = [dataclasses.astuple(e) for e in get_recursive_composite_type_info(an)]
    assert type_infos == [(tuple, [], ChildMod.REPEAT, (int,))]


def test_structure_error_union():
    an = get_annotations(h)["a"]
    assert get_first_structure_error(1, an) is None

    # tricky: constraint error but structure is OK
    assert get_first_structure_error(-1.0, an) is None

    assert get_first_structure_error([], an) is not None
    assert get_first_structure_error("string", an) is not None


def test_constraints_error_union():
    an = get_annotations(h)["a"]
    assert not get_constraints_errors(0.0, an)
    assert get_constraints_errors(-1.0, an)


# ((<0.0) x (int)) + ((>0.0) x ((<0.0) x (int)) + (>0.0)))
type PosFloat = Annotated[float, Gt(0.0)]
type NegFloat = Annotated[float, Lt(0.0)]
type NegAndInt = tuple[NegFloat, int]
type NegAndIntOrPos = NegAndInt | PosFloat
type Complex = NegAndInt | tuple[PosFloat, NegAndIntOrPos]


def recursive_union(a: Complex):  # pragma: no cover
    pass


def test_complex():
    an = get_annotations(recursive_union)["a"]
    assert not get_constraints_errors((-1.0, 1), an)
    assert get_constraints_errors((1.0, 1), an)
    assert not get_constraints_errors((1.0, (-1.0, 1)), an)
    assert get_constraints_errors((1.0, (1.0, 1)), an)
    assert not get_constraints_errors((1.0, 1.0), an)

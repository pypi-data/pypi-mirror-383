import pytest
from contractme import annotated
from typing import Annotated, TypeAlias
from annotated_types import (
    Lt,
    Le,
    Gt,
    Ge,
    Interval,
    MultipleOf,
    MinLen,
    MaxLen,
    Len,
    Timezone,
    doc,  # type: ignore
    # for some reason this triggers pyright?
    # predicates
    LowerCase,
)
import functools
import operator
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def test_int():
    @annotated
    def birthday(age: int):
        return age + 1

    assert birthday(1) == 2
    with pytest.raises(AssertionError):
        birthday(1.0)  # type: ignore
        # mistyped on purpose


def test_return_int():
    @annotated
    def birthday(age) -> int:
        return age + 1

    assert birthday(1) == 2
    with pytest.raises(AssertionError):
        birthday(1.0)


def test_bound_typevar():
    @annotated
    def add[I: int](age: I, added: I) -> int:
        return int(age + added)

    assert add(1, 1) == 2
    with pytest.raises(AssertionError):
        add(1.0, 1.0)  # type: ignore
        # mistyped on purpose


Age = Annotated[int, Ge(1)]


def test_precondition():
    @annotated
    def birthday(age: Age) -> Age:
        return age + 1

    assert birthday(1) == 2

    with pytest.raises(AssertionError):
        birthday(0)

    with pytest.raises(AssertionError):
        birthday(1.0)  # type: ignore
        # mistyped on purpose


def test_postcondition():
    @annotated
    def antibirthday(age: Age) -> Age:
        return age - 1

    with pytest.raises(AssertionError):
        antibirthday(1)


def test_postcondition_int():
    @annotated
    def birthday(age) -> Age:
        return age + 1.0

    with pytest.raises(AssertionError):
        birthday(1)


Lt0: TypeAlias = Annotated[int, Lt(0)]


def test_Lt():
    @annotated
    def f(lt0: Lt0):
        pass

    f(-1)

    with pytest.raises(AssertionError):
        f(0)


Le0: TypeAlias = Annotated[int, Le(0)]


def test_Le():
    @annotated
    def f(le0: Le0):
        pass

    f(0)

    with pytest.raises(AssertionError):
        f(1)


Ge0: TypeAlias = Annotated[int, Ge(0)]


def test_Ge():
    @annotated
    def f(ge0: Ge0):
        pass

    f(0)

    with pytest.raises(AssertionError):
        f(-1)


Gt0: TypeAlias = Annotated[int, Gt(0)]


def test_Gt():
    @annotated
    def f(gt0: Gt0):
        pass

    f(1)

    with pytest.raises(AssertionError):
        f(0)


Lt0_partial: TypeAlias = Annotated[int, functools.partial(operator.lt, 0)]


def test_functools_partial_Lt():
    @annotated
    def f(_: Lt0_partial):
        pass

    f(-1)

    with pytest.raises(AssertionError):
        f(0)


Le0_partial: TypeAlias = Annotated[int, functools.partial(operator.le, 0)]


def test_functools_partial_Le():
    @annotated
    def f(_: Le0_partial):
        pass

    f(0)

    with pytest.raises(AssertionError):
        f(1)


Ge0_partial: TypeAlias = Annotated[int, functools.partial(operator.ge, 0)]


def test_functools_partial_Ge():
    @annotated
    def f(_: Ge0_partial):
        pass

    f(0)

    with pytest.raises(AssertionError):
        f(-1)


Gt0_partial: TypeAlias = Annotated[int, functools.partial(operator.gt, 0)]


def test_functools_partial_Gt():
    @annotated
    def f(gt0: Gt0_partial):
        pass

    f(1)

    with pytest.raises(AssertionError):
        f(0)


class MyInt_gt:
    def __init__(self, val):
        self.val = val

    def __gt__(self, other: "MyInt_gt"):
        return self.val > other.val


Gt0_MyInt: TypeAlias = Annotated[MyInt_gt, Gt(MyInt_gt(0))]


def test_Gt_custom():
    @annotated
    def f_Gt0(gt0: Gt0_MyInt):
        pass

    f_Gt0(MyInt_gt(1))

    with pytest.raises(AssertionError):
        f_Gt0(MyInt_gt(0))


class MyInt_lt:
    def __init__(self, val):
        self.val = val

    def __lt__(self, other: "MyInt_lt"):
        return self.val < other.val


Lt0_MyInt: TypeAlias = Annotated[MyInt_lt, Lt(MyInt_lt(0))]


def test_Lt_custom():
    @annotated
    def f_Lt0(lt0: Lt0_MyInt):
        pass

    f_Lt0(MyInt_lt(-1))

    with pytest.raises(AssertionError):
        f_Lt0(MyInt_lt(0))


class MyInt_ge:
    def __init__(self, val):
        self.val = val

    def __ge__(self, other: "MyInt_ge"):
        return self.val >= other.val


Ge0_MyInt: TypeAlias = Annotated[MyInt_ge, Ge(MyInt_ge(0))]


def test_Ge_custom():
    @annotated
    def f_Ge0(ge0: Ge0_MyInt):
        pass

    f_Ge0(MyInt_ge(0))

    with pytest.raises(AssertionError):
        f_Ge0(MyInt_ge(-1))


Vacuous: TypeAlias = Annotated[int, Interval()]


def test_vacuous_Interval():
    @annotated
    def f(_: Vacuous):
        pass

    f(0)


Gt0_Interval: TypeAlias = Annotated[int, Interval(gt=0)]


def test_Interval_only_gt():
    @annotated
    def f(_: Gt0_Interval):
        pass

    f(1)
    f(1000)

    with pytest.raises(AssertionError):
        f(0)


Gt0Lt2: TypeAlias = Annotated[int, Interval(gt=0, lt=2)]


def test_Interval_gt_lt():
    @annotated
    def f(_: Gt0Lt2):
        pass

    f(1)

    with pytest.raises(AssertionError):
        f(0)
    with pytest.raises(AssertionError):
        f(2)


Ge0Lt2: TypeAlias = Annotated[int, Interval(ge=0, lt=2)]


def test_Interval_ge_lt():
    @annotated
    def f(_: Ge0Lt2):
        pass

    f(0)
    f(1)

    with pytest.raises(AssertionError):
        f(-1)
    with pytest.raises(AssertionError):
        f(2)


Gt0Le2: TypeAlias = Annotated[int, Interval(gt=0, le=2)]


def test_Interval_gt_le():
    @annotated
    def f(_: Gt0Le2):
        pass

    f(1)
    f(2)

    with pytest.raises(AssertionError):
        f(0)
    with pytest.raises(AssertionError):
        f(3)


Ge0Le2: TypeAlias = Annotated[int, Interval(ge=0, le=2)]


def test_Interval_ge_le():
    @annotated
    def f(_: Ge0Le2):
        pass

    f(0)
    f(2)

    with pytest.raises(AssertionError):
        f(-1)
    with pytest.raises(AssertionError):
        f(3)


Mult3: TypeAlias = Annotated[int, MultipleOf(3)]


def test_MultipleOf():
    @annotated
    def f(_: Mult3):
        pass

    f(-3)
    f(0)
    f(3)
    f(6)

    with pytest.raises(AssertionError):
        f(-1)
    with pytest.raises(AssertionError):
        f(1)


NotEmpty: TypeAlias = Annotated[str, MinLen(1)]


def test_MinLen():
    @annotated
    def f(_: NotEmpty):
        pass

    f("a")
    with pytest.raises(AssertionError):
        f("")


SmallStr: TypeAlias = Annotated[str, MaxLen(3)]


def test_MaxLen():
    @annotated
    def f(_: SmallStr):
        pass

    f("")
    f("aaa")

    with pytest.raises(AssertionError):
        f("aaaa")


BigramOrTrigram: TypeAlias = Annotated[str, Len(2, 3)]


def test_Len():
    @annotated
    def f(_: BigramOrTrigram):
        pass

    f("aa")
    f("aaa")

    with pytest.raises(AssertionError):
        f("")
    with pytest.raises(AssertionError):
        f("aaaa")


TzAware_Ellipsis: TypeAlias = Annotated[datetime, Timezone(...)]


def test_Timezone_datetime_Ellipsis():
    @annotated
    def f(_: TzAware_Ellipsis):
        pass

    f(datetime.now(tz=ZoneInfo("Europe/Paris")))

    with pytest.raises(AssertionError):
        f(datetime.now(tz=None))


NaiveDatetime: TypeAlias = Annotated[datetime, Timezone(None)]


def test_Timezone_datetime_None():
    @annotated
    def f(_: NaiveDatetime):
        pass

    f(datetime.now(tz=None))

    with pytest.raises(AssertionError):
        f(datetime.now(timezone.utc))


AtParisTz_str: TypeAlias = Annotated[datetime, Timezone("Europe/Paris")]


def test_Timezone_datetime_str():
    @annotated
    def f(_: AtParisTz_str):
        pass

    f(datetime.now(tz=ZoneInfo("Europe/Paris")))

    with pytest.raises(AssertionError):
        f(datetime.now(timezone.utc))


AtParisTz_ZoneInfo: TypeAlias = Annotated[datetime, Timezone(ZoneInfo("Europe/Paris"))]


def test_Timezone_datetime_ZoneInfo():
    @annotated
    def f(_: AtParisTz_ZoneInfo):
        pass

    f(datetime.now(tz=ZoneInfo("Europe/Paris")))

    with pytest.raises(AssertionError):
        f(datetime.now(timezone.utc))


def test_predicate_input():
    @annotated
    def f(_: LowerCase):
        pass

    f("aaaa")
    with pytest.raises(AssertionError):
        f("aaaA")


def test_predicate_return():
    @annotated
    def f(a: str) -> LowerCase:
        return a

    f("aaaa")
    with pytest.raises(AssertionError):
        f("aaaA")


Documented: TypeAlias = Annotated[int, doc("Well, it's a integer")]


def test_Doc():
    @annotated
    def f(a: Documented) -> Documented:
        return a

    assert f(1) == 1
    with pytest.raises(AssertionError):
        f("aaaA")  # type: ignore


def test_list_of_annotated():
    @annotated
    def f(a: Annotated[list[Documented], MinLen(1)]) -> Documented:
        return a[0]

    assert f([1, 2]) == 1
    with pytest.raises(AssertionError):
        f(None)  # type: ignore
    with pytest.raises(AssertionError):
        f("aaaA")  # type: ignore
    with pytest.raises(AssertionError):
        f([1, "aaaA"])  # type: ignore


def test_tuple_of_length_ge_1():
    @annotated
    def f(a: Annotated[tuple[Documented, ...], MinLen(1)]) -> Documented:
        return a[0]

    assert f((1,)) == 1
    assert f((1, 2)) == 1
    with pytest.raises(AssertionError):
        f(tuple())  # type: ignore
    with pytest.raises(AssertionError):
        f([1, 2])  # type: ignore


def test_empty_tuple():
    @annotated
    def f(a: tuple[()]):
        pass

    assert f(tuple()) is None
    with pytest.raises(AssertionError):
        f(None)  # type: ignore
    with pytest.raises(AssertionError):
        f((1,))  # type: ignore


def test_list_of_tuple_of_annotated():
    @annotated
    def f(a: Annotated[list[tuple[Documented, Documented]], MinLen(1)]) -> Documented:
        return a[0][0]

    assert f([(1, 2)]) == 1

    with pytest.raises(AssertionError):
        f([(1,)])  # type: ignore
    with pytest.raises(AssertionError):
        f([(1, 2.0)])  # type: ignore


def test_list_of_tuple_of_constrained():
    @annotated
    def f(a: Annotated[list[tuple[Annotated[int, Gt(0)], int]], MinLen(1)]) -> Documented:
        return a[0][0]

    assert f([(1, 0)]) == 1

    with pytest.raises(AssertionError):
        f([(0, 0)])  # type: ignore


def test_tuple_ellipsis():
    @annotated
    def f(a: tuple[int, ...]):
        return a[-1]

    assert f((1, 0)) == 0

    with pytest.raises(AssertionError):
        f((0, 1.0))  # type: ignore


type IntGt0 = Annotated[int, Gt(0)]


def test_type_alias():
    @annotated
    def f(a: IntGt0):
        return a

    assert f(1) == 1
    with pytest.raises(AssertionError):
        f(1.0)  # type: ignore
    with pytest.raises(AssertionError):
        f(0)  # type: ignore


def test_union_types():
    @annotated
    def f(a: int | None):
        return a

    assert f(None) is None
    assert f(0) == 0
    with pytest.raises(AssertionError):
        f(1.0)  # type: ignore


type RecList = list[RecList]


def test_recursive_type():
    @annotated
    def f(a: RecList):
        actual = a
        while actual:
            actual = actual[0]
        return actual

    e = []

    assert f([[[e]]]) is e
    assert f([[[e], e], e]) is e
    with pytest.raises(AssertionError):
        _ = f([[[e]], 1])  # type: ignore
    with pytest.raises(AssertionError):
        _ = f([[[e, None]]])  # type: ignore


type MutRec1 = list[MutRec2]
type MutRec2 = MutRec1 | int


def test_mutually_recursive_types():
    @annotated
    def f(a: MutRec1):
        actual = a
        while isinstance(actual, list):
            actual = actual[0]
        return actual

    assert f([[[0]]]) == 0


type PropsMap = dict[str, Annotated[float, Gt(0.0)]]


def test_dict():
    @annotated
    def get_val(kv: PropsMap, key: str, default: float = 0.0) -> float:
        if key in kv:
            return kv[key]
        else:
            return default

    assert get_val({"toto": 10.0}, "toto") == 10.0
    assert get_val({"toto": 10.0}, "tata") == 0.0

    with pytest.raises(AssertionError):
        _ = get_val({"toto": 10}, "toto")

    with pytest.raises(AssertionError):
        _ = get_val({"toto": 0.0}, "toto")


type Height = Annotated[float, Ge(0.0)]
type InternalPressureFlyingAtm = Annotated[float, Interval(ge=0.0, le=1.0)]
type Depth = Annotated[float, Le(0.0)]
type InternalPressureDivingAtm = Annotated[float, Ge(1.0)]
type FlyOrDivePressureAtm = tuple[Height, InternalPressureFlyingAtm] | tuple[
    Depth, InternalPressureDivingAtm
]


def test_advanced_union():
    @annotated
    def pressure_is_ok(p: FlyOrDivePressureAtm):
        if p[0] == 0.0:
            # on the ground: pressure should be constant
            return p[1] == 1.0
        elif p[0] > 0.0:
            # flying: keep pressure high
            return p[1] >= 0.75
        elif p[0] < 0.0:
            # diving: keep pressure low
            return p[1] <= 1.25

    # at ground
    assert pressure_is_ok((0.0, 1.0))
    assert not pressure_is_ok((0.0, 0.5))
    assert not pressure_is_ok((0.0, 2.0))

    with pytest.raises(AssertionError):  # type: ignore
        _ = pressure_is_ok((0.0, -1.0))

    # in flight
    assert pressure_is_ok((1000.0, 0.9))
    assert not pressure_is_ok((1000.0, 0.5))
    with pytest.raises(AssertionError):  # type: ignore
        _ = pressure_is_ok((1000.0, 1.1))

    # diving
    assert pressure_is_ok((-1000.0, 1.1))
    assert not pressure_is_ok((-1000.0, 1.5))
    with pytest.raises(AssertionError):  # type: ignore
        _ = pressure_is_ok((-1000.0, 0.9))

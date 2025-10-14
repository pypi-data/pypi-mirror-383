import sys
import datetime
import zoneinfo
import functools
import operator
from enum import Enum, auto
from dataclasses import dataclass
import types
import typing
from typing import (
    Annotated,
    Any,
    Callable,
    Iterable,
    TypeAliasType,
    TypeVar,
    get_origin,
    get_args,
)
import annotated_types

assert sys.version_info >= (3, 12)

# Stolen from typeshed
type ClassInfo = type | types.UnionType | tuple[ClassInfo, ...]
type AnnotationForm = Any

type Constraint = functools.partial | Any
# More specifically: some are taken into account (annotated-types),
# some are not (open world: it's yours and IDC about it)
# maybe they could be redispatched to extensions in the future? closing the
# world so that any malformed constraint could be detected?
type NormalizedConstraint = Any
# partial functions are re-contracted to annotated-types constraints


def normalize_constraint(constraint: Constraint) -> NormalizedConstraint:
    if isinstance(constraint, functools.partial):
        # https://github.com/annotated-types/annotated-types?tab=readme-ov-file#gt-ge-lt-le
        match constraint.func, constraint.args:
            case operator.lt, (n,):
                n = annotated_types.Lt(n)
            case operator.le, (n,):
                n = annotated_types.Le(n)
            case operator.gt, (n,):
                n = annotated_types.Gt(n)
            case operator.ge, (n,):
                n = annotated_types.Ge(n)
            case _:  # pragma: no cover
                raise NotImplementedError(constraint)
        return n
    else:
        return constraint


def get_all_constraint_errors(val, constraints: list[Constraint]) -> list[NormalizedConstraint]:
    if not constraints:
        return []
    else:
        failing = []
        for constraint_denorm in constraints:
            constraint = normalize_constraint(constraint_denorm)
            match constraint:
                case annotated_types.Interval(gt=None, lt=None, ge=None, le=None):
                    # null range
                    check = True
                case annotated_types.Gt(gt=gt) | annotated_types.Interval(
                    gt=gt, lt=None, ge=None, le=None
                ):
                    check = val > gt
                case annotated_types.Lt(lt=lt) | annotated_types.Interval(
                    lt=lt, gt=None, ge=None, le=None
                ):
                    check = val < lt
                case annotated_types.Ge(ge=ge) | annotated_types.Interval(
                    ge=ge, lt=None, gt=None, le=None
                ):
                    check = val >= ge
                case annotated_types.Le(le=le) | annotated_types.Interval(
                    le=le, lt=None, ge=None, gt=None
                ):
                    check = val <= le
                case annotated_types.Interval(gt=gt, lt=lt, ge=None, le=None):
                    check = gt < val < lt
                case annotated_types.Interval(ge=ge, lt=lt, gt=None, le=None):
                    check = ge <= val < lt
                case annotated_types.Interval(gt=gt, le=le, ge=None, lt=None):
                    check = gt < val <= le
                case annotated_types.Interval(ge=ge, le=le, gt=None, lt=None):
                    check = ge <= val <= le
                case annotated_types.MultipleOf(multiple_of=multiple_of):
                    check = val % multiple_of == 0
                case annotated_types.MinLen(min_length=min_length) | annotated_types.Len(
                    min_length=min_length, max_length=None
                ):
                    check = min_length <= len(val)
                case annotated_types.MaxLen(max_length=max_length) | annotated_types.Len(
                    max_length=max_length, min_length=None
                ):
                    check = len(val) <= max_length
                case annotated_types.Len(min_length=min_length, max_length=max_length):
                    assert min_length is not None and max_length is not None
                    check = min_length <= len(val) <= max_length
                case annotated_types.Timezone(tz=tz):
                    if tz is None:
                        check = val.tzinfo is None
                    elif tz is Ellipsis:
                        check = val.tzinfo is not None
                    elif isinstance(tz, datetime.tzinfo):
                        check = val.tzinfo == tz
                    elif isinstance(tz, str):
                        check = val.tzinfo == zoneinfo.ZoneInfo(tz)
                    else:  # pragma: no cover
                        raise NotImplementedError(f"tz being {tz.__class__.__name__}")
                case annotated_types.Predicate(func=func):
                    check = func(val)
                case _:
                    check = True

            if not check:
                failing.append(constraint)
        return failing


def resolve_type(t: AnnotationForm) -> AnnotationForm:
    """
    Best-effort type resolution, this will remove as many
    type var or alias as possible.
    """
    alias = []
    while isinstance(t, (TypeVar, TypeAliasType)):
        if t in alias:
            # circular definition
            break
        else:
            alias.append(t)

        if isinstance(t, TypeAliasType):
            t = t.__value__
        elif isinstance(t, TypeVar):
            t = t.__bound__ or Any
    return t


class ChildMod(Enum):
    NONE = auto()
    REPEAT = auto()  # 0..n
    REPEAT_KV = auto()  # {0: a, 1: b ...}
    OPTION = auto()  # A | B | C


type ConstraintSet = list[Any]


@dataclass
class CompositeTypeInfo:
    origin: ClassInfo
    constraints: ConstraintSet
    child_mod: ChildMod
    children: tuple[AnnotationForm, ...]

    def __init__(self, t: AnnotationForm):
        origin = get_origin(t) or t
        self.constraints = list()
        while origin is Annotated:
            self.constraints += get_args(t)[1:]
            t = resolve_type(get_args(t)[0])
            origin = get_origin(t) or t
        self.origin = origin
        args = get_args(t)
        if self.origin == tuple and len(args) == 2 and args[1] == Ellipsis:
            self.child_mod = ChildMod.REPEAT
            self.children = (args[0],)
        elif self.origin == list:
            assert (
                len(args) == 1
            ), "Cannot have list[T1, T2...] must either be list[T1] or list[tuple[T1, T2]]"
            self.child_mod = ChildMod.REPEAT
            self.children = args
        elif self.origin in (dict,):
            self.child_mod = ChildMod.REPEAT_KV
            self.children = args
        elif self.origin in (types.UnionType, typing.Union):
            self.child_mod = ChildMod.OPTION
            self.children = args
        else:
            self.child_mod = ChildMod.NONE
            self.children = args


def get_recursive_composite_type_info(an: AnnotationForm) -> Iterable[CompositeTypeInfo]:
    to_visit = [an]

    while to_visit:
        t = resolve_type(to_visit.pop(0))
        r = CompositeTypeInfo(t)
        if r.child_mod == ChildMod.NONE:
            to_visit += r.children
        yield r


@dataclass
class ErrorsCollector:
    _context: list
    _errors: list[str]
    _local_error: bool

    def __init__(self):
        self._context = []
        self._errors = []
        self._local_error = False

    def set_context(self, type_info):
        self._context.append(type_info.origin)

    def _append_error(self, msg):
        self._errors.append(f"in {self._context}: {msg}")

    def check_cond(self, cond: bool, message: str):
        self._local_error = not cond
        if self._local_error:
            self._append_error(message)

    def is_ok(self) -> bool:
        return not self._errors

    def locally_ok(self) -> bool:
        return not self._local_error

    def maybe_first_error(self) -> str | None:
        return None if not self._errors else self._errors[0]

    def all_errors(self) -> list[str]:
        return self._errors

    def clear_errors(self) -> None:
        self._errors = []


def get_first_structure_error(value, an, recursive_type_info=None) -> str | None:
    struct = ErrorsCollector()

    if recursive_type_info is None:
        recursive_type_info = get_recursive_composite_type_info(an)

    check_values = [value]
    for type_info in recursive_type_info:
        # Struct check
        val = check_values.pop(0)
        struct.set_context(type_info)
        is_sequence = type_info.origin in (list, tuple)
        if type_info.child_mod == ChildMod.OPTION:
            found = False
            for c in type_info.children:
                err = get_first_structure_error(val, c)
                if not err:
                    found = True
                    break
            struct.check_cond(found, f"{val} does not match any of {type_info.children}")
        else:
            struct.check_cond(
                isinstance(val, type_info.origin),
                f"expect {type_info.origin} got {val.__class__.__name__}",
            )
            if struct.is_ok():
                if type_info.child_mod == ChildMod.REPEAT:
                    assert len(type_info.children) == 1
                    for v in val:
                        err = get_first_structure_error(v, type_info.children[0])
                        struct.check_cond(not err, str(err))
                        if not struct.is_ok():
                            break
                elif type_info.child_mod == ChildMod.REPEAT_KV:
                    assert len(type_info.children) == 2
                    for v in val.items():
                        err = get_first_structure_error(v[0], type_info.children[0])
                        struct.check_cond(not err, str(err))
                        err = get_first_structure_error(v[1], type_info.children[1])
                        struct.check_cond(not err, str(err))
                        if not struct.is_ok():
                            break
                elif is_sequence:
                    # depth-first
                    struct.check_cond(
                        len(val) == len(type_info.children),
                        f"not the right number of children: "
                        f"expect {len(type_info.children)} got {len(val)}",
                    )
                    if struct.is_ok():
                        check_values = list(val) + check_values

        if not struct.is_ok():
            break
    assert not check_values, f"bug! values remains to be checked ({check_values}) for {value} {an}"
    return struct.maybe_first_error()


def get_constraints_errors(
    value, an, recursive_type_info: Iterable[CompositeTypeInfo] | None = None
):
    constraints = ErrorsCollector()

    def only_valid(rti: Iterable[CompositeTypeInfo]):
        # unimplemented
        yield from rti

    if recursive_type_info is None:
        recursive_type_info = get_recursive_composite_type_info(an)

    check_values = [value]
    for type_info in only_valid(recursive_type_info):
        # Constraints check
        val = check_values.pop(0)
        if type_info.child_mod == ChildMod.OPTION:
            constraint_failures = None
            for child in type_info.children:
                # check structure, again, very innefficient
                if get_first_structure_error(val, child):
                    continue
                err = get_constraints_errors(val, child)
                constraints.check_cond(not err, "tried option {child_type_info}: {err}")
                if not err:
                    # found a config that works
                    constraints.clear_errors()
                    break
        else:
            is_sequence = type_info.origin in (list, tuple)
            constraint_failures = get_all_constraint_errors(val, type_info.constraints)
            constraints.check_cond(
                not constraint_failures,
                f"{val!r} failed constraint {constraint_failures}",
            )
            if constraints.locally_ok():
                # check only if parent constraints are already ok
                if type_info.child_mod == ChildMod.REPEAT:
                    assert len(type_info.children) == 1
                    for v in val:
                        err = get_constraints_errors(v, type_info.children[0])
                        constraints.check_cond(not err, str(err))
                elif type_info.child_mod == ChildMod.REPEAT_KV:
                    assert len(type_info.children) == 2
                    for v in val.items():
                        err = get_constraints_errors(v[0], type_info.children[0])
                        constraints.check_cond(not err, str(err))
                        err = get_constraints_errors(v[1], type_info.children[1])
                        constraints.check_cond(not err, str(err))
                elif is_sequence:
                    # depth-first
                    check_values = list(val) + check_values

    assert not check_values, f"bug! values remains to be checked ({check_values}) for {value} {an}"
    return constraints.all_errors()

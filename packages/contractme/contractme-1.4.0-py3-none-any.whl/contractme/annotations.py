import sys
from typing import get_type_hints
from inspect import get_annotations
from contractme.contracting import precondition, postcondition
from contractme.typecheck import (
    get_first_structure_error,
    get_constraints_errors,
    resolve_type,
    AnnotationForm,
)


def get_types_and_annotations_errors(value, an):
    """
    Checks the structure and annotations of data provided compared to the annotations.

    The structure is checked first, then iif it is valid, the annotations are. This allows
    for a better error messaging: you first provide a correct structure, then correct values.
    """
    # we visit all of the possible nodes depth-first
    # for each one, we check its type, and we delegate any annotation check
    # then we loop over all these annotations, and we check them as well
    # this has a potentially big runtime cost for nested option or recursive
    # types.
    struct_err = get_first_structure_error(value, an)
    if struct_err:
        return f"structure is malformed: {struct_err}"
    else:
        constraints_err = get_constraints_errors(value, an)
        if constraints_err:
            return "structure ok, but value does not match constraints: " + ", ".join(
                constraints_err
            )
        else:
            return None


def annotated(f):
    def check_annotated_arg(arg_name, arg_an: AnnotationForm):
        constraints = getattr(arg_an, "__metadata__", tuple())
        t = resolve_type(arg_an)
        if constraints:
            msg = f"{arg_name} should be instance of {t} under constraints {constraints}"
        else:
            msg = f"{arg_name} should be instance of {t}"

        if arg_name == "return":
            cond_arg_name = "result"
            cond_f = postcondition
        else:
            cond_arg_name = arg_name
            cond_f = precondition

        def chk(**kw):
            err = get_types_and_annotations_errors(kw[cond_arg_name], arg_an)
            if err:
                print(f"arg {cond_arg_name}: {err}", file=sys.stderr)

            return err is None

        cond = cond_f(chk, msg)
        return cond

    ths = get_type_hints(f)
    ans = get_annotations(f)

    for n, t_or_typevar in ths.items():
        f = check_annotated_arg(n, ans[n])(f)

    return f

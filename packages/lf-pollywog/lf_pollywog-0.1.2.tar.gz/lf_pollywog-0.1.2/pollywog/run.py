import copy
from pollywog.core import CalcSet, If, IfRow
import re


import math
import numpy as np


# Leapfrog-like math functions
def log(n, base=10):
    return math.log(n, base)


def ln(n):
    return math.log(n)


def exp(n):
    return math.exp(n)


def sqrt(n):
    return math.sqrt(n)


def abs(n):
    return abs(n)


# Trigonometric functions
def sin(x):
    return math.sin(x)


def cos(x):
    return math.cos(x)


def tan(x):
    return math.tan(x)


def asin(x):
    return math.asin(x)


def acos(x):
    return math.acos(x)


def atan(x):
    return math.atan(x)


# Limits and rounding
def min_(*args):
    return min(args)


def max_(*args):
    return max(args)


def clamp(n, lower, upper=None):
    if upper is not None:
        return max(lower, min(n, upper))
    return max(n, lower)


def round_(n, dp=None):
    if dp is not None:
        return round(n, dp)
    return round(n)


def roundsf(n, sf):
    if n == 0:
        return 0
    from math import log10, floor

    return round(n, -int(floor(log10(abs(n)))) + (sf - 1))


def floor_(n):
    return math.floor(n)


def ceiling(n):
    return math.ceil(n)


def truncate(n):
    return int(n)


# Text functions
def concat(*args):
    return "".join(str(a) for a in args)


def startswith(t, prefix):
    return str(t).startswith(prefix)


def endswith(t, suffix):
    return str(t).endswith(suffix)


def contains(t, part):
    return part in str(t)


def like(t, pattern):
    import re

    return re.search(pattern, str(t)) is not None


def regexp(t, pattern):
    import re

    return re.search(pattern, str(t)) is not None


def min(*args):
    return min_(*args)


def max(*args):
    return max_(*args)


def round(n, dp=None):
    return round_(n, dp)


def floor(n):
    return floor_(n)


LEAPFROG_ENV = {
    "log": log,
    "ln": ln,
    "exp": exp,
    "sqrt": sqrt,
    "abs": abs,
    "pi": math.pi,
    "e": math.e,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "min": min_,
    "max": max_,
    "clamp": clamp,
    "round": round_,
    "roundsf": roundsf,
    "floor": floor_,
    "ceiling": ceiling,
    "truncate": truncate,
    "concat": concat,
    "startswith": startswith,
    "endswith": endswith,
    "contains": contains,
    "like": like,
    "regexp": regexp,
}


def run_calcset(
    calcset, inputs=None, dataframe=None, assign_results=True, output_variables=False
):
    """
    Evaluate a CalcSet with external inputs or a pandas DataFrame.
    Returns a dict of results (if inputs provided) or a DataFrame (if dataframe provided).
    Pandas is only required if using DataFrame input/output.
    By default, only calculations, categories, and filters are output (Leapfrog-like).
    Set output_variables=True to include variables in output (for debugging).
    """

    # Helper to evaluate an expression or If object
    def eval_expr(expr, context):
        if isinstance(expr, str):
            if not expr.strip():
                return None

            # Replace [var] with context["var"] using regex
            def repl(m):
                var = m.group(1)
                return f"context[{repr(var)}]"

            expr_eval = re.sub(r"\[([^\]]+)\]", repl, expr)
            try:
                # Provide Leapfrog-like environment for eval
                return eval(expr_eval, {"context": context, **LEAPFROG_ENV}, context)
            except Exception:
                return None
        elif isinstance(expr, If):
            for row in expr.rows:
                cond = eval_expr(row.condition[0], context) if row.condition else True
                if cond:
                    return eval_expr(row.value[0], context)
            if expr.otherwise:
                return eval_expr(expr.otherwise[0], context)
            return None
        elif isinstance(expr, IfRow):
            # Should not be evaluated directly, only as part of If
            return None
        else:
            return expr

    # Dependency resolution
    sorted_items = calcset.topological_sort().items

    def run_single(context):
        results = {}
        for item in sorted_items:
            # If item is a Variable, assign its value from context or inputs directly
            if getattr(item, "item_type", None) == "variable":
                results[item.name] = context.get(item.name, None)
                continue
            child_results = []
            for child in item.children:
                child_results.append(eval_expr(child, {**context, **results}))
            results[item.name] = child_results[0] if child_results else None
        # Filter output according to output_variables flag
        item_type_map = {
            item.name: getattr(item, "item_type", None) for item in sorted_items
        }
        if not output_variables:
            return {
                k: v for k, v in results.items() if item_type_map.get(k) != "variable"
            }
        return results

    if dataframe is not None:
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for DataFrame input/output. Please install pandas or use dict inputs."
            )
        df = dataframe.copy()
        for idx, row in df.iterrows():
            context = dict(row)
            results = run_single(context)
            for k, v in results.items():
                df.at[idx, k] = v
        # Remove variable columns if output_variables is False
        if not output_variables:
            variable_names = [
                item.name
                for item in sorted_items
                if getattr(item, "item_type", None) == "variable"
            ]
            df = df.drop(columns=variable_names, errors="ignore")
        return df
    else:
        context = inputs if inputs is not None else {}
        return run_single(context)


# Pandas DataFrame extension accessor
try:
    import pandas as pd

    @pd.api.extensions.register_dataframe_accessor("pw")
    class PollywogAccessor:
        def __init__(self, pandas_obj):
            self._obj = pandas_obj

        def run(self, calcset, assign_results=True):
            """
            Run a CalcSet on this DataFrame, returning a copy with results assigned.
            """
            return run_calcset(
                calcset, dataframe=self._obj, assign_results=assign_results
            )

except ImportError:
    pass

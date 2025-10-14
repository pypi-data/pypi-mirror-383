from .core import If, IfRow, Number, Category
from .utils import ensure_variables


def Sum(*variables, name=None, comment=None):
    """
    Create a Number representing the sum of the given variables.

    Args:
        *variables: Variable names (as strings) to sum, e.g. "Au", "Ag", or a single list of variable names as strings.
        name (str, optional): Name for the output variable. If None, defaults to "sum_<var1>_<var2>_..."
        comment (str, optional): Optional comment for the calculation.

    Returns:
        Number: A pollywog Number representing the sum calculation.

    Example:
        >>> Sum("Au", "Ag", name="sum_Au_Ag")
    """
    if not variables:
        raise ValueError("At least one variable must be provided.")
    if len(variables) == 1 and isinstance(variables[0], (list, tuple)):
        variables = variables[0]
    if name is None:
        name = "sum_" + "_".join(variables)
    expr = f"({' + '.join(f'[{v}]' for v in variables)})"
    return Number(
        name, [expr], comment_equation=comment or f"Sum of {', '.join(variables)}"
    )


def Product(*variables, name=None, comment=None):
    """
    Create a Number representing the product of the given variables.

    Args:
        *variables: Variable names (as strings) to multiply, e.g. "Au", "Ag", or a single list of variable names as strings.
        name (str, optional): Name for the output variable. If None, defaults to "prod_<var1>_<var2>_..."
        comment (str, optional): Optional comment for the calculation.

    Returns:
        Number: A pollywog Number representing the product calculation.

    Example:
        >>> Product("Au", "Ag", name="prod_Au_Ag")
    """
    if not variables:
        raise ValueError("At least one variable must be provided.")
    if len(variables) == 1 and isinstance(variables[0], (list, tuple)):
        variables = variables[0]
    if name is None:
        name = "prod_" + "_".join(variables)
    expr = f"({' * '.join(f'[{v}]' for v in variables)})"
    return Number(
        name, [expr], comment_equation=comment or f"Product of {', '.join(variables)}"
    )


def Normalize(variable, min_value, max_value, name=None, comment=None):
    """
    Create a Number that normalizes a variable to [0, 1] given min and max values.

    Args:
        variable (str): Variable name to normalize.
        min_value (float): Minimum value for normalization.
        max_value (float): Maximum value for normalization.
        name (str, optional): Name for the output variable. If None, defaults to "norm_<variable>".
        comment (str, optional): Optional comment for the calculation.

    Returns:
        Number: A pollywog Number representing the normalization calculation.

    Example:
        >>> Normalize("Au", 0, 10, name="norm_Au")
    """
    if name is None:
        name = f"norm_{variable}"
    expr = f"([{variable}] - {min_value}) / ({max_value} - {min_value})"
    return Number(
        name,
        [expr],
        comment_equation=comment
        or f"Normalize {variable} to [0, 1] using min={min_value}, max={max_value}",
    )


def Average(*variables, name=None, comment=None):
    """
    Create a Number representing the average of the given variables.

    Args:
        *variables: Variable names (as strings) to average, e.g. "Au", "Ag", or a single list of variable names as strings.
        name (str, optional): Name for the output variable. If None, defaults to "avg_<var1>_<var2>_..."
        comment (str, optional): Optional comment for the calculation.

    Returns:
        Number: A pollywog Number representing the average calculation.

    Example:
        >>> Average("Au", "Ag", name="avg_Au_Ag")
    """
    if not variables:
        raise ValueError("At least one variable must be provided.")
    if len(variables) == 1 and isinstance(variables[0], list):
        variables = variables[0]
    if name is None:
        name = "avg_" + "_".join(variables)
    expr = f"({' + '.join(f'[{v}]' for v in variables)}) / {len(variables)}"
    return Number(
        name, [expr], comment_equation=comment or f"Average of {', '.join(variables)}"
    )


def WeightedAverage(variables, weights, name=None, comment=None):
    """
    Create a Number representing the weighted average of variables.

    Args:
        variables (list of str): Variable names to average, e.g. ["Au", "Ag", "Cu"]
        weights (list of float or string): Corresponding weights for each variable, either constant values ( e.g. [0.5, 0.3, 0.2]) or variable names (e.g. ["w1", "w2", "w3"]).
        name (str, optional): Name for the output variable. If None, defaults to "wavg_<var1>_<var2>_..."
        comment (str, optional): Optional comment for the calculation.

    Returns:
        Number: A pollywog Number representing the weighted average calculation.

    Example:
        >>> WeightedAverage(["Au", "Ag"], [0.7, 0.3], name="wavg_Au_Ag")
    """
    if not variables or not weights or len(variables) != len(weights):
        raise ValueError("variables and weights must be non-empty and of equal length.")
    if name is None:
        name = "wavg_" + "_".join(variables)
    weights = ensure_variables(weights)
    sum_weights = " + ".join(weights)
    weighted_terms = [f"[{v}] * {w}" for v, w in zip(variables, weights)]
    expr = f"({' + '.join(weighted_terms)}) / ({sum_weights})"
    return Number(
        name,
        [expr],
        comment_equation=comment
        or f"Weighted average of {', '.join(variables)} with weights {weights}",
    )


def Scale(variable, factor, name=None, comment=None):
    """
    Create a Number that multiplies a variable by a factor.

    Args:
        variable (str): Variable name to scale.
        factor (float or str): Scaling factor (can be a constant or another variable).
        name (str, optional): Name for the output variable. If None, defaults to "scale_<variable>".
        comment (str, optional): Optional comment for the calculation.

    Returns:
        Number: A pollywog Number representing the scaled variable.

    Example:
        >>> Scale("Au", 2, name="Au_scaled")
    """
    if name is None:
        name = f"scale_{variable}"
    factor_expr = f"[{factor}]" if isinstance(factor, str) else str(factor)
    expr = f"[{variable}] * {factor_expr}"
    return Number(
        name, [expr], comment_equation=comment or f"Scale {variable} by {factor}"
    )


def CategoryFromThresholds(variable, thresholds, categories, name=None, comment=None):
    """
    Create a Category assigning labels based on value thresholds.

    Args:
        variable (str): Variable to threshold.
        thresholds (list of float): Threshold values (must be sorted ascending).
        categories (list of str): Category labels (len(categories) == len(thresholds) + 1).
        name (str, optional): Name for the output category.
        comment (str, optional): Optional comment for the calculation.

    Returns:
        Category: A pollywog Category assigning labels based on thresholds.

    Example:
        >>> CategoryFromThresholds("Au", [0.5, 1.0], ["Low", "Medium", "High"], name="Au_class")
    """
    if len(categories) != len(thresholds) + 1:
        raise ValueError("categories must have one more element than thresholds")
    rows = []
    prev = None
    for i, threshold in enumerate(thresholds):
        if prev is None:
            cond = f"[{variable}] <= {threshold}"
        else:
            cond = f"([{variable}] > {prev}) and ([{variable}] <= {threshold})"
        rows.append(([cond], [categories[i]]))
        prev = threshold
    # Otherwise case
    otherwise = [categories[-1]]
    if_block = If([IfRow(cond, val) for cond, val in rows], otherwise=otherwise)
    if name is None:
        name = f"class_{variable}"
    return Category(
        name,
        [if_block],
        comment_equation=comment or f"Classify {variable} by thresholds {thresholds}",
    )

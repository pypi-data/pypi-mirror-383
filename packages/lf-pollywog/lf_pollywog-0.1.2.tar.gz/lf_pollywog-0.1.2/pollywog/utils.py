def ensure_list(x) -> list:
    """
    Ensure the input is a list. If not, wrap it in a list.

    Args:
        x (Any): Input value or list.
    Returns:
        list: The input as a list.
    """
    if not isinstance(x, list):
        x = [x]
    return x


def ensure_str_list(x):
    """
    Ensure the input is a list of strings, padding with empty strings if needed.

    Args:
        x (Any): Input value or list.
    Returns:
        list: List of strings, padded with empty strings if necessary.
    """
    if not isinstance(x, list):
        x = [x]
    if isinstance(x, list):
        if not isinstance(x[0], str):
            x = [""] + x
        if not isinstance(x[-1], str):
            x = x + [""]
    return x


def to_dict(items, guard_strings=False):
    """
    Convert a list of items to their dictionary representations if possible.

    Args:
        items (list): List of items or single item.
        guard_strings (bool): If True, pad with empty strings if first/last are not strings.
    Returns:
        list: List of dicts or items, possibly padded with empty strings.
    """
    out = [
        item.to_dict() if hasattr(item, "to_dict") else item
        for item in ensure_list(items)
    ]
    if guard_strings:
        if not isinstance(out[0], str):
            out = [""] + out
        if not isinstance(out[-1], str):
            out = out + [""]
    return out


def is_number(v):
    """
    Check if the input can be converted to a float (i.e., is a number).

    Args:
        v (Any): Input value.
    Returns:
        bool: True if input is a number, False otherwise.
    """
    try:
        float(v)
        return True
    except (ValueError, TypeError):
        return False


def ensure_brackets(var):
    """
    Ensure the variable name is wrapped in brackets [var].

    Args:
        var (str): Variable name.
    Returns:
        str: Variable name wrapped in brackets.
    """
    var = var.strip()
    if not (var.startswith("[") and var.endswith("]")):
        var = f"[{var}]"
    return var


def ensure_variables(variables):
    """
    Ensures that each item in the input is formatted as a variable.
    For each item in `variables`, if the item is a number, it is converted to a string.
    Otherwise, it is passed to `ensure_brackets` to ensure proper bracket formatting.
    Args:
        variables (Any): A single variable or a list of variables to be processed.
    Returns:
        list: A list of formatted variable strings.
    """

    return [
        f"{v}" if is_number(v) else ensure_brackets(v) for v in ensure_list(variables)
    ]

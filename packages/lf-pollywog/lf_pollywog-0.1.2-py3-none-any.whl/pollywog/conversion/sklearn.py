from ..core import If, IfRow, Variable, Number, Category

try:
    import sklearn
except ImportError:
    raise ImportError(
        "scikit-learn is required for conversion. Please install it via 'pip install scikit-learn'."
    )


# Classification and Regression Trees

from sklearn import tree, ensemble


def convert_tree(
    tree_model,
    feature_names,
    target_name,
    flat=False,
    comment_equation=None,
    output_type=None,
):
    tree_ = tree_model.tree_
    feature_name = [
        feature_names[i] if i != tree._tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

    is_classifier = hasattr(tree_model, "classes_")
    classes = None
    if is_classifier:
        classes = tree_model.classes_

    if flat:
        # Create a flat list of conditions and values
        conditions = []
        values = []

        def recurse_flat(node, current_conditions):
            if tree_.feature[node] != tree._tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                left_conditions = current_conditions + [f"[{name}] <= {threshold}"]
                right_conditions = current_conditions + [f"[{name}] > {threshold}"]
                recurse_flat(tree_.children_left[node], left_conditions)
                recurse_flat(tree_.children_right[node], right_conditions)
            else:
                value = (
                    tree_.value[node][0][0]
                    if not is_classifier
                    else classes[tree_.value[node][0].argmax()]
                )
                value = f'"{value}"' if isinstance(value, str) else str(value)
                conditions.append(
                    " and ".join(current_conditions) if current_conditions else "True"
                )
                values.append(value)

        recurse_flat(0, [])
        if_rows = [IfRow([cond], [val]) for cond, val in zip(conditions, values)]
        if_rows = If(if_rows, otherwise=["blank"])
    else:
        # Create nested If structure
        def recurse(node):
            if tree_.feature[node] != tree._tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                left = recurse(tree_.children_left[node])
                right = recurse(tree_.children_right[node])
                return If(IfRow(f"[{name}] <= {threshold}", left), right)
            else:
                value = (
                    tree_.value[node][0][0]
                    if not is_classifier
                    else classes[tree_.value[node][0].argmax()]
                )
                value = f'"{value}"' if isinstance(value, str) else str(value)
                return value

        if_rows = recurse(0)

    if comment_equation is None:
        comment_equation = f"Converted from {tree_model.__class__.__name__}"

    if output_type is not None:
        return output_type(target_name, if_rows, comment_equation=comment_equation)

    if isinstance(tree_model, tree.DecisionTreeRegressor):
        return Number(target_name, if_rows, comment_equation=comment_equation)
    elif isinstance(tree_model, tree.DecisionTreeClassifier):
        return Category(target_name, if_rows, comment_equation=comment_equation)
    else:
        raise ValueError("Unsupported tree model type")


def convert_forest(
    forest_model, feature_names, target_name, flat=False, comment_equation=None
):
    """Convert a RandomForestRegressor or RandomForestClassifier to a Pollywog Number or Category.

    Args:
        forest_model: A fitted RandomForestRegressor or RandomForestClassifier from scikit-learn
        feature_names: List of feature names used in the model
        target_name: Name of the target variable to create
        flat: Whether to create flattened if expressions (default: False)
        comment_equation: Optional comment for the generated equation

    Returns:
        A Pollywog Number (for regression) or Category (for classification)
    """
    if not isinstance(
        forest_model, (ensemble.RandomForestRegressor, ensemble.RandomForestClassifier)
    ):
        raise ValueError(
            "forest_model must be a RandomForestRegressor or RandomForestClassifier"
        )

    # Convert each tree in the forest
    trees = [
        convert_tree(
            estimator,
            feature_names,
            f"{target_name}_tree_{i}",
            flat=flat,
            comment_equation=f"Tree {i} from {forest_model.__class__.__name__}",
            output_type=Variable,
        )
        for i, estimator in enumerate(forest_model.estimators_)
    ]

    # Average predictions for regression or majority vote for classification
    if isinstance(forest_model, ensemble.RandomForestRegressor):
        # For regression, create an equation that averages the tree outputs
        tree_outputs = " + ".join([f"[{t.name}]" for t in trees])
        equation = f"({tree_outputs}) / {len(trees)}"
        return trees + [
            Number(
                target_name,
                [equation],
                comment_equation=f"Averaged output from {len(trees)} trees in {forest_model.__class__.__name__}",
            )
        ]
    elif isinstance(forest_model, ensemble.RandomForestClassifier):
        # For classification, create an equation that does majority voting
        tree_outputs = " + ".join([f"[{t.name}]" for t in trees])
        equation = f"round(({tree_outputs}) / {len(trees)})"
        return trees + [
            Category(
                target_name,
                [equation],
                comment_equation=f"Majority vote from {len(trees)} trees in {forest_model.__class__.__name__}",
            )
        ]


# Linear Models
from sklearn import linear_model


def convert_linear_model(lm_model, feature_names, target_name):
    coefs = lm_model.coef_
    intercept = lm_model.intercept_

    def format_float(val):
        return f"{float(val):.6f}"

    terms = [format_float(intercept)] if intercept != 0 else []
    for coef, feature in zip(coefs, feature_names):
        if coef != 0:
            terms.append(f"{format_float(coef)} * [{feature}]")

    equation = " + ".join(terms) if terms else "0"
    return Number(
        target_name,
        [equation],
        comment_equation=f"Converted from {lm_model.__class__.__name__}",
    )


# Pre Processing

from pollywog.helpers import (
    Average,
    Sum,
    Product,
    Normalize,
    WeightedAverage,
    Scale,
    CategoryFromThresholds,
)
from pollywog.core import Number


def test_average_helper():
    n = Average("Au", "Ag", name="avg_Au_Ag")
    assert isinstance(n, Number)
    assert n.name == "avg_Au_Ag"
    assert "/ 2" in n.children[0]
    assert "[Au]" in n.children[0] and "[Ag]" in n.children[0]


def test_sum_helper():
    n = Sum("Au", "Ag", name="sum_Au_Ag")
    assert isinstance(n, Number)
    assert n.name == "sum_Au_Ag"
    assert "[Au]" in n.children[0] and "[Ag]" in n.children[0]
    assert "+" in n.children[0]


def test_product_helper():
    n = Product("Au", "Ag", name="prod_Au_Ag")
    assert isinstance(n, Number)
    assert n.name == "prod_Au_Ag"
    assert "[Au]" in n.children[0] and "[Ag]" in n.children[0]
    assert "*" in n.children[0]


def test_normalize_helper():
    n = Normalize("Au", 0, 10, name="norm_Au")
    assert isinstance(n, Number)
    assert n.name == "norm_Au"
    assert "[Au]" in n.children[0]
    assert "/ (10 - 0)" in n.children[0]


def test_weighted_average_helper():
    # Test with constant weights
    n = WeightedAverage(["Au", "Ag"], [0.7, 0.3], name="wavg_Au_Ag")
    assert isinstance(n, Number)
    assert n.name == "wavg_Au_Ag"
    assert "[Au] * 0.7" in n.children[0]
    assert "[Ag] * 0.3" in n.children[0]
    assert "/ (0.7 + 0.3)" in n.children[0] or "/ (1.0)" in n.children[0]

    # Test with variable weights
    n2 = WeightedAverage(["Au", "Ag"], ["w1", "w2"], name="wavg_Au_Ag_varw")
    assert isinstance(n2, Number)
    assert n2.name == "wavg_Au_Ag_varw"
    assert "[Au] * [w1]" in n2.children[0]
    assert "[Ag] * [w2]" in n2.children[0]
    assert "/ ([w1] + [w2])" in n2.children[0]


def test_scale_helper():
    n = Scale("Au", 2, name="Au_scaled")
    assert isinstance(n, Number)
    assert n.name == "Au_scaled"
    assert "[Au] * 2" in n.children[0]

    n2 = Scale("Ag", "factor", name="Ag_scaled")
    assert isinstance(n2, Number)
    assert n2.name == "Ag_scaled"
    assert "[Ag] * [factor]" in n2.children[0]


def test_category_from_thresholds_helper():
    n = CategoryFromThresholds(
        "Au", [0.5, 1.0], ["Low", "Medium", "High"], name="Au_class"
    )
    assert n.name == "Au_class"
    # Should contain If block
    assert hasattr(n, "children")
    assert "Classify Au by thresholds [0.5, 1.0]" in n.comment_equation

def test_query_with_external_variable():
    from pollywog.core import CalcSet, Variable, Number

    a = Variable(name="a", children=["foo"])
    b = Number(name="b1", children=["[a] + 1"])
    c = Number(name="b2", children=["[b1] + 2"])
    cs = CalcSet([a, b, c])
    prefix = "b"
    # Should select items whose name starts with prefix
    result = cs.query("name.startswith(@prefix)")
    names = [item.name for item in result.items]
    assert set(names) == {"b1", "b2"}


def test_query_with_multiple_external_vars():
    from pollywog.core import CalcSet, Variable, Number

    a = Variable(name="a", children=["foo"])
    b = Number(name="b1", children=["[a] + 1"])
    c = Number(name="b2", children=["[b1] + 2"])
    cs = CalcSet([a, b, c])
    prefix = "b"
    suffix = "2"
    # Should select items whose name starts with prefix and ends with suffix
    result = cs.query("name.startswith(@prefix) and name.endswith(@suffix)")
    names = [item.name for item in result.items]
    assert names == ["b2"]


def test_topological_sort_simple():
    from pollywog.core import Number, Variable, CalcSet

    a = Variable(name="a", children=["foo"])
    b = Number(name="b", children=["[a] + 1"])
    c = Number(name="c", children=["[b] + 2"])
    cs = CalcSet([c, b, a])
    sorted_cs = cs.topological_sort()
    names = [item.name for item in sorted_cs.items]
    assert names == ["a", "b", "c"]


def test_topological_sort_external_dep():
    from pollywog.core import Number, Variable, CalcSet

    a = Variable(name="a", children=["foo"])
    b = Number(name="b", children=["[external] + 1"])
    cs = CalcSet([b, a])
    sorted_cs = cs.topological_sort()
    names = [item.name for item in sorted_cs.items]
    assert set(names) == {"a", "b"}


def test_topological_sort_cycle():
    from pollywog.core import Number, CalcSet

    a = Number(name="a", children=["[b] + 1"])
    b = Number(name="b", children=["[a] + 2"])
    cs = CalcSet([a, b])
    import pytest

    with pytest.raises(ValueError):
        cs.topological_sort()


def test_item_rename():
    num = Number(name="n1", children=["[x] + 1"])
    # Rename item name only
    num2 = num.rename(name="n2")
    assert num2.name == "n2"
    assert num2.children == ["[x] + 1"]
    # Rename variable inside children
    num3 = num.rename(variables={"x": "y"})
    assert num3.children == ["[y] + 1"]
    # Rename both name and variable
    num4 = num.rename(name="n3", variables={"x": "z"})
    assert num4.name == "n3"
    assert num4.children == ["[z] + 1"]


def test_calcset_rename_items_and_variables():
    num = Number(name="n1", children=["[x] + 1"])
    var = Variable(name="x", children=["foo"])
    filt = Filter(name="f1", children=["[x] > 0"])
    cs = CalcSet([num, var, filt])
    # Rename item names
    cs2 = cs.rename(items={"n1": "n2", "f1": "f2"})
    assert cs2.items[0].name == "n2"
    assert cs2.items[2].name == "f2"
    # Rename variable references in children
    cs3 = cs.rename(variables={"x": "y"})
    assert cs3.items[0].children == ["[y] + 1"]
    assert cs3.items[2].children == ["[y] > 0"]
    # Rename both items and variables
    cs4 = cs.rename(items={"n1": "n3"}, variables={"x": "z"})
    assert cs4.items[0].name == "n3"
    assert cs4.items[0].children == ["[z] + 1"]
    assert cs4.items[2].children == ["[z] > 0"]


def test_rename_with_regex():
    num = Number(name="prefix_n1", children=["[var_x] + 1"])
    var = Variable(name="var_x", children=["foo"])
    cs = CalcSet([num, var])
    # Rename with regex
    cs2 = cs.rename(
        items={r"^prefix_": "renamed_"}, variables={r"^var_": "newvar_"}, regex=True
    )
    assert cs2.items[0].name == "renamed_n1"
    assert cs2.items[0].children == ["[newvar_x] + 1"]
    assert cs2.items[1].name == "newvar_x"


def test_rename_nested_if():
    ifrow = IfRow(condition=["[x] > 0"], value=["[x] + 1"])
    ifexpr = If(rows=[ifrow], otherwise=["[x] - 1"])
    num = Number(name="n1", children=[ifexpr])
    cs = CalcSet([num])
    cs2 = cs.rename(variables={"x": "y"})
    nested_if = cs2.items[0].children[0]
    assert isinstance(nested_if, If)
    assert nested_if.rows[0].condition == ["[y] > 0"]
    assert nested_if.rows[0].value == ["[y] + 1"]
    assert nested_if.otherwise == ["[y] - 1"]


import pytest
from pollywog.core import CalcSet, Number

from pollywog.core import Variable, Filter, If, IfRow, Category


def test_number_to_dict_and_from_dict():
    num = Number(name="n1", children=["1+2"])
    d = num.to_dict()
    num2 = Number.from_dict(d)
    assert num2.name == "n1"
    assert num2.children == ["1+2"]


def test_variable_and_filter():
    var = Variable(name="v1", children=["foo"])
    filt = Filter(name="f1", children=["bar"])
    assert var.to_dict()["type"] == "variable"
    assert filt.to_dict()["type"] == "filter"


def test_category():
    cat = Category(name="cat1", children=["'A'"])
    d = cat.to_dict()
    assert d["calculation_type"] == "string"


def test_ifrow_and_if():
    ifrow = IfRow(condition=["[x] > 0"], value=["1"])
    d = ifrow.to_dict()
    ifrow2 = IfRow.from_dict(d)
    assert ifrow2.condition == ["[x] > 0"]
    assert ifrow2.value == ["1"]

    # Test If with three-parameter mode
    ifexpr3 = If("[x] > 0", "1", "0")
    assert isinstance(ifexpr3, If)
    assert isinstance(ifexpr3.rows[0], IfRow)
    assert ifexpr3.rows[0].condition == "[x] > 0"
    assert ifexpr3.rows[0].value == "1"
    assert ifexpr3.otherwise == "0" or ifexpr3.otherwise == ["0"]

    ifexpr = If(rows=[ifrow], otherwise=["0"])
    d2 = ifexpr.to_dict()
    ifexpr2 = If.from_dict(d2)
    assert isinstance(ifexpr2, If)
    assert isinstance(ifexpr2.rows[0], IfRow)
    assert ifexpr2.otherwise == ["0"]


def test_calcset_serialization():
    num = Number(name="n1", children=["1+2"])
    var = Variable(name="v1", children=["foo"])
    cs = CalcSet([num, var])
    json_str = cs.to_json()
    cs2 = CalcSet.from_dict(cs.to_dict())
    assert isinstance(cs2, CalcSet)
    assert len(cs2.items) == 2


def test_calcset_repr():
    num = Number(name="n1", children=["1+2"])
    cs = CalcSet([num])
    s = repr(cs)
    assert s.startswith("{")


def test_calcset_add_multiple():
    num1 = Number(name="a", children=["2"])
    num2 = Number(name="b", children=["3"])
    var = Variable(name="v", children=["foo"])
    cs1 = CalcSet([num1])
    cs2 = CalcSet([num2, var])
    cs3 = cs1 + cs2
    assert len(cs3.items) == 3
    assert cs3.items[2].name == "v"


def test_copy_independence():
    num = Number(name="n1", children=["1+2"])
    num_copy = num.copy()
    assert isinstance(num_copy, Number)
    assert num_copy.name == num.name
    assert num_copy.children == num.children
    num_copy.name = "n2"
    num_copy.children[0] = "3+4"
    assert num.name == "n1"
    assert num.children[0] == "1+2"

    var = Variable(name="v1", children=["foo"])
    var_copy = var.copy()
    var_copy.name = "v2"
    assert var.name == "v1"

    filt = Filter(name="f1", children=["bar"])
    filt_copy = filt.copy()
    filt_copy.name = "f2"
    assert filt.name == "f1"

    cat = Category(name="cat1", children=["'A'"])
    cat_copy = cat.copy()
    cat_copy.name = "cat2"
    assert cat.name == "cat1"

    ifrow = IfRow(condition=["[x] > 0"], value=["1"])
    ifrow_copy = ifrow.copy()
    ifrow_copy.condition[0] = "[x] < 0"
    assert ifrow.condition[0] == "[x] > 0"

    ifexpr = If(rows=[ifrow], otherwise=["0"])
    ifexpr_copy = ifexpr.copy()
    ifexpr_copy.rows[0].condition[0] = "[x] == 0"
    assert ifexpr.rows[0].condition[0] == "[x] > 0"

    cs = CalcSet([num, var, filt, cat, ifrow, ifexpr])
    cs_copy = cs.copy()
    cs_copy.items[0].name = "changed"
    assert cs.items[0].name == "n1"


def test_error_handling():
    # Wrong type for CalcSet.from_dict
    with pytest.raises(ValueError):
        CalcSet.from_dict({"type": "not-calcset", "items": []})
    # Unknown item type
    with pytest.raises(ValueError):
        CalcSet.from_dict({"type": "calculation-set", "items": [{"type": "unknown"}]})


def test_ifrow_invalid_type():
    with pytest.raises(ValueError):
        IfRow.from_dict({"type": "not_if_row"})


def test_if_invalid_type():
    with pytest.raises(ValueError):
        If.from_dict({"type": "not_if"})


def test_calcset_to_dict():
    num = Number(name="test_num", children=["1+1"])
    calcset = CalcSet([num])
    d = calcset.to_dict()
    assert d["type"] == "calculation-set"
    assert isinstance(d["items"], list)
    assert d["items"][0]["name"] == "test_num"


def test_calcset_add():
    num1 = Number(name="a", children=["2"])
    num2 = Number(name="b", children=["3"])
    cs1 = CalcSet([num1])
    cs2 = CalcSet([num2])
    cs3 = cs1 + cs2
    assert len(cs3.items) == 2
    assert cs3.items[0].name == "a"
    assert cs3.items[1].name == "b"

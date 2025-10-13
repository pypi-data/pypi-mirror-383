import pytest
from pollywog.core import CalcSet, Variable, Number, If, IfRow
from pollywog.run import run_calcset


def test_import_run():
    # Just test that run.py imports without error
    assert True


def test_run_calcset_with_dict():
    a = Variable(name="a", children=[""])
    b = Number(name="b", children=["[a] + 1"])
    c = Number(name="c", children=["[b] * 2"])
    cs = CalcSet([a, b, c])
    inputs = {"a": 3}
    results = run_calcset(cs, inputs=inputs)
    assert "a" not in results  # Variable should not be in output by default
    assert results["b"] == 4
    assert results["c"] == 8
    # Debug mode: output_variables=True
    debug_results = run_calcset(cs, inputs=inputs, output_variables=True)
    assert debug_results["a"] == 3
    assert debug_results["b"] == 4
    assert debug_results["c"] == 8


def test_run_calcset_with_if():
    a = Variable(name="a", children=[""])
    ifrow1 = IfRow(condition=["[a] > 0"], value=["1"])
    ifrow2 = IfRow(condition=["[a] <= 0"], value=["-1"])
    ifexpr = If(rows=[ifrow1, ifrow2], otherwise=["0"])
    b = Number(name="b", children=[ifexpr])
    cs = CalcSet([a, b])
    results = run_calcset(cs, inputs={"a": 2})
    assert "a" not in results
    assert results["b"] == 1
    results = run_calcset(cs, inputs={"a": -2})
    assert results["b"] == -1
    results = run_calcset(cs, inputs={"a": 0})
    assert results["b"] == -1
    # Debug mode
    debug_results = run_calcset(cs, inputs={"a": 2}, output_variables=True)
    assert debug_results["a"] == 2
    assert debug_results["b"] == 1


def test_run_calcset_with_dataframe():
    import pandas as pd

    a = Variable(name="a", children=[""])
    b = Number(name="b", children=["[a] + 1"])
    cs = CalcSet([a, b])
    df = pd.DataFrame({"a": [1, 2, 3]})
    result_df = run_calcset(cs, dataframe=df)
    assert list(result_df["b"]) == [2, 3, 4]
    assert "a" not in result_df.columns  # Variable column should be dropped
    # Debug mode
    debug_df = run_calcset(cs, dataframe=df, output_variables=True)
    assert "a" in debug_df.columns
    assert list(debug_df["a"]) == [1, 2, 3]


def test_pw_accessor():
    import pandas as pd

    b = Number(name="b", children=["[a] + 1"])
    cs = CalcSet([b])
    df = pd.DataFrame({"a": [10, 20]})
    result_df = df.pw.run(cs)
    assert list(result_df["b"]) == [11, 21]

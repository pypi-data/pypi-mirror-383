# Automating Leapfrog Workflows with Pollywog – An Independent Open-Source Tool

[![DOI](https://zenodo.org/badge/1071742254.svg)](https://doi.org/10.5281/zenodo.17313856)

Professionals using Seequent solutions for geological modeling and resource estimation often work with .lfcalc files. These files can be repetitive to manage and prone to manual errors. This is especially true when dealing with conditional logic, domain-based dilution calculations, or predictive model integration.

Pollywog was developed to support this technical audience. It is a Python package that enables:

- Programmatic reading and writing of .lfcalc files, making calculations more standardized and reproducible
- Automation of complex workflows, including conditional equations and post-processing of results
- Integration with machine learning models via scikit-learn, allowing classifiers or regressions to be applied directly within Leapfrog calculations
- Creation of reusable scripts, which can be versioned and audited, providing greater control over modeling processes

Pollywog aims to reduce time spent on manual tasks, minimize input errors, and increase efficiency in geological modeling.

The documentation includes practical examples and tutorials to help technical teams get started quickly.

If you work with Leapfrog and are looking to optimize your workflows, Pollywog is worth exploring.

Pollywog is still very much a work in progress, so take care in its use and make sure to not have anything important open and not saved in Leapfrog while testing it out. Also, please report any issues you encounter. Suggestions and contributions are very welcome!

## Legal Disclaimer

Pollywog is an independent open-source tool developed to support the automation of workflows involving .lfcalc files used in Leapfrog software by Seequent.
This tool does not perform reverse engineering, does not modify Leapfrog, and does not access its source code or proprietary libraries. Pollywog operates exclusively on user-generated files and is designed to complement Leapfrog through external automation.

Important:
- Pollywog is not affiliated with, endorsed by, or sponsored by Seequent or any company associated with Leapfrog
- Use of this tool does not violate Leapfrog’s license terms or Seequent’s policies
- Users are encouraged to review Leapfrog’s terms of use before integrating Pollywog into commercial or corporate environments
- The author is not responsible for any misuse of the tool that may breach Seequent’s licensing terms


## Installation

Install from pypi (not available yet, but soon):

```bash
pip install lf_pollywog
```

Or install the latest development version from GitHub:

```bash
pip install git+https://github.com/endarthur/pollywog.git
```

## Usage

### Reading and Writing `.lfcalc` files

```python
import pollywog as pw
calcset = pw.CalcSet.read_lfcalc("path/to/file.lfcalc")
calcset.to_lfcalc("output.lfcalc")
```

### Creating a Simple Calculation Set

```python
from pollywog.core import Number, CalcSet
calcset = CalcSet([
    Number(name="Au_final", children=["clamp([Au_est], 0)"]),
    Number(name="Ag_final", children=["clamp([Ag_est], 0)"])
])
calcset.to_lfcalc("postprocessed.lfcalc")
```

### Converting a scikit-learn model

Currently supports decision trees (both classification and regression) and linear models:

```python
from pollywog.conversion.sklearn import convert_tree
from sklearn.tree import DecisionTreeRegressor
import numpy as np
X = np.array([[0.2, 1.0, 10], [0.5, 2.0, 20]])
y = np.array([0.7, 0.8])
feature_names = ["Cu_final", "Au_final", "Ag_final"]
reg = DecisionTreeRegressor(max_depth=2)
reg.fit(X, y)
recovery_calc = convert_tree(reg, feature_names, "recovery_ml")
CalcSet([recovery_calc]).to_lfcalc("recovery_ml.lfcalc")
```

For more advanced workflows (domain dilution, conditional logic, economic value, combining CalcSets, etc.), see the Jupyter notebooks in the `examples/` folder of this repository or the documentation at https://pollywog.readthedocs.io/en/latest/.

## Querying CalcSets

Pollywog provides a powerful query method for filtering items in a `CalcSet`, inspired by pandas' DataFrame.query. You can use Python-like expressions to select items based on their attributes and external variables.

### Syntax
- Use item attributes (e.g., `name`, `item_type`) in expressions.
- Reference external variables using `@var` syntax (e.g., `name.startswith(@prefix)`).
- Supported helpers: `len`, `any`, `all`, `min`, `max`, `sorted`, `re`, `str`.

### Examples

```python
# Select items whose name starts with 'Au'
calcset.query('name.startswith("Au")')

# Select items whose name starts with an external variable 'prefix'
prefix = "Ag"
calcset.query('name.startswith(@prefix)')

# Select items with more than one child
calcset.query('len(children) > 1')

# Use regular expressions
calcset.query('re.match(r"^A", name)')
```

### Notes
- External variables (`@var`) are resolved from the caller's scope or passed as keyword arguments.
- Only items matching the query expression are returned in the new `CalcSet`.

## License

MIT License

<!-- ## Authors

See `AUTHORS` file or repository contributors. -->

## Contributions

Contributions are very welcome!
If you'd like to collaborate on Pollywog, whether through bug fixes, feature enhancements, new use cases, or documentation, please follow these steps:

- Fork the repository
- Create a feature branch (git checkout -b feature-name)
- Make your changes and commit (git commit -m 'Add new feature')
- Submit a pull request with a clear explanation of your changes

Before contributing, please:
- Ensure your changes align with the project’s goals
- Maintain consistent code style
- Test your modifications whenever possible

Feel free to open an issue if you have questions or suggestions.

## Acknowledgements

Thanks to Debora Roldão for helping with organization of the project, documentation and design, Eduardo Takafuji for the initial discussion of the feasability of this all those years ago and Jessica da Matta for support and sanity checks along the way.

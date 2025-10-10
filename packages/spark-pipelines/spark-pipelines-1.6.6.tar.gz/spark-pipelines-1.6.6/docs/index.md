# spark-pipelines Documentation

## Overview

**spark-pipelines** is a Python package designed for validating Spark DataFrames against data quality rules. It provides a set of decorators that can be applied to functions that load data, allowing users to enforce data quality checks seamlessly. The package supports various validation strategies, including:

- **expect**: Validates DataFrames and prints a report of the validation results.
- **expect_drop**: Validates DataFrames and returns a filtered DataFrame containing only valid records.
- **expect_fail**: Validates DataFrames and raises an exception if any validation rule fails.
- **expect_quarantine**: Validates DataFrames and optionally quarantines failed records to a specified location or table.

## Features

- **Data Quality Validation**: Easily validate your Spark DataFrames against custom rules.
- **Flexible Quarantine Options**: Quarantine failed records to a specified path or table.
- **Comprehensive Reporting**: Get detailed reports on validation results, including passed and failed counts.
- **Customizable Decorators**: Use different decorators to suit your data validation needs.

## Usage

To use the package, simply decorate your data loading functions with the desired validation decorator. For example:

```python
from spark_pipelines import DataQuality

rules = {
    "Employee ID should be greater than 2": "emp_id > 2",
    "Name should not be null": "fname IS NOT NULL"
}

@DataQuality.expect(rules)
def load_employee_df():
    return spark.read.table("employee")

df = load_employee_df()
```

## Installation

You can install the package via pip:

```
pip install spark-pipelines
```

## Documentation

Comprehensive documentation is available in the `docs` directory, including detailed usage examples and explanations of each validation method.

## Contribution

Contributions are welcome! Please refer to the `CHANGELOG.md` for the history of changes and the `LICENSE` file for licensing information.
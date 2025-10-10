# Detailed Usage Instructions for spark-pipelines

## Overview

The **spark-pipelines** package is designed to facilitate data quality validation for Spark DataFrames. By using decorators, users can easily enforce data quality rules on their data loading functions, ensuring that only valid data is processed. This package is particularly useful for data engineers and data scientists who work with large datasets and need to maintain high data quality standards.

## Installation

To install the **spark-pipelines** package, you can use pip:

```bash
pip install spark-pipelines
```

## Usage

### Basic Example

To get started, you can define your data quality rules in a dictionary format, where the keys are human-readable descriptions of the rules, and the values are SQL filter expressions. Then, you can decorate your data loading functions with the appropriate validation decorator.

Here is a simple example:

```python
from spark_pipelines import DataQuality

dq = DataQuality(
    spark=spark,
    job_name="employee_ingestion_job"
                )

# Define your data quality rules
rules = {
    "Employee ID should be greater than 2": "emp_id > 2",
    "Name should not be null": "fname IS NOT NULL"
}

# Use the expect decorator to validate the DataFrame
@dq.expect(rules)
def load_employee_df():
    return spark.read.table("employee")

# Load the DataFrame and validate it
df = load_employee_df()
```

### Validation Strategies

The package provides several decorators for different validation strategies:

1. **expect**: This decorator validates the DataFrame and prints a report of the validation results. If any rule fails, the DataFrame is still returned.

   ```python
   @DataQuality.expect(rules)
   def load_employee_df():
       return spark.read.table("employee")

   ```

2. **expect_drop**: This decorator validates the DataFrame and returns a filtered DataFrame containing only the valid records. Failed records are excluded.

   ```python
   @DataQuality.expect_drop(rules)
   def load_employee_df():
       return spark.read.table("employee")

   ```

3. **expect_fail**: This decorator validates the DataFrame and raises an exception if any validation rule fails. This is useful for stopping the pipeline execution when data quality issues are detected.

   ```python
   @DataQuality.expect_fail(rules)
   def load_employee_df():
       return spark.read.table("employee")

   ```

4. **expect_quarantine**: This decorator validates the DataFrame and optionally quarantines failed records to a specified location or table. You can specify either a path or a table name for storing the quarantined records.

   ```python
   from spark_pipelines import DataQuality
   dq = DataQuality(
        spark=spark,
        job_name="employee_ingestion_job",
        dq_table_name="data_quality.default.employee_dq",
        quarantine_table="data_quality.default.employee_qr",
        quarantine_format='delta'
                 )

   @dq.expect_quarantine(rules)
   def load_employee_df():
       return spark.read.table("employee")

   ```


### Documentation

For more detailed usage examples and explanations of each validation method, refer to the comprehensive documentation available in the `docs` directory of the package.

### Contribution

Contributions to the **spark-pipelines** package are welcome! Please check the `CHANGELOG.md` for the history of changes and the `LICENSE` file for licensing information. If you have suggestions or improvements, feel free to submit a pull request.

By following these instructions, users can effectively utilize the **spark-pipelines** package to ensure high data quality in their Spark applications.
# filepath: spark-pipelines/src/spark_pipelines/validators.py

"""
validators.py

This module provides additional validation functions and classes that can be used to enhance the data quality checks
in the spark-pipelines package. It is designed to work seamlessly with the DataQuality class and its decorators.

The validators can be used to create custom validation rules or extend the existing validation capabilities provided
by the DataQuality class.

Usage
-----
To use the validators in conjunction with the DataQuality class, you can define custom validation functions and
apply them as decorators to your data loading functions.

Example:
---------
from spark_pipelines import DataQuality
from spark_pipelines.validators import custom_validator

@DataQuality.expect(rules)
@custom_validator
def load_employee_df():
    return spark.read.table("employee")

df = load_employee_df()
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

def custom_validator(func):
    """
    A custom validator decorator that can be applied to data loading functions.

    This decorator can be used to implement additional validation logic that is not covered by the standard
    DataQuality decorators.

    Parameters
    ----------
    func : function
        The function to be decorated.

    Returns
    -------
    function
        The decorated function with additional validation logic.
    """
    def wrapper(*args, **kwargs):
        df: DataFrame = func(*args, **kwargs)

        # Example validation: Check if 'emp_id' is unique
        if df.select("emp_id").distinct().count() != df.count():
            raise ValueError("Validation failed: 'emp_id' must be unique.")

        # Additional validation logic can be added here

        return df

    return wrapper

# Additional custom validation functions can be defined below as needed.
# filepath: spark-pipelines/src/spark_pipelines/types.py

from typing import Any, Dict, List, Tuple

# Define custom types for enhanced type safety and clarity

# A type for validation rules, where each rule is a tuple of a description and a condition
ValidationRule = Tuple[str, str]

# A type for the validation results, which includes the rule, counts, and status
ValidationResult = Dict[str, Any]

# A type for a list of validation rules
ValidationRules = List[ValidationRule]

# A type for a DataFrame, which can be used to annotate DataFrame parameters and return types
DataFrameType = Any  # Replace with the actual DataFrame type from your Spark library if needed

# Additional custom types can be defined here as needed for the package's functionality
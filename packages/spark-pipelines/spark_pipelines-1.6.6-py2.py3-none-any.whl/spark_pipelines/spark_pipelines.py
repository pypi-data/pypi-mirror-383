class DataQuality:

    from typing import List, Dict, Optional, Callable
    from pyspark.sql import SparkSession, Row, DataFrame
    from pyspark.sql.functions import current_timestamp, expr, col, lit


    def __init__(
        self, 
        spark: SparkSession, 
        job_name: Optional[str] = None,
        dq_table_name: Optional[str] = None,
        quarantine_location: Optional[str] = None,
        quarantine_table: Optional[str] = None,
        quarantine_format: str = "parquet"   # default format
                 ):
        self.spark = spark
        self.job_name = job_name
        self.dq_table_name = dq_table_name
        self.quarantine_location = quarantine_location
        self.quarantine_table = quarantine_table
        self.quarantine_format = quarantine_format
        self.job_run_id = str(self.__generate_uuid())
    

    def __generate_uuid(self):
        import random
        random_bits = [random.getrandbits(50) for _ in range(8)]
        return f"{random_bits[0]:04x}{random_bits[1]:04x}-{random_bits[2]:04x}-{random_bits[3]:04x}-{random_bits[4]:04x}-{random_bits[5]:04x}{random_bits[6]:04x}{random_bits[7]:04x}"


    def __dq_results_to_table(
        self,
        results: List[Dict],
            ) -> None:
        from pyspark.sql import Row
        from pyspark.sql.functions import current_timestamp
        
        row_results = [Row(**r) for r in results]
        results_df = self.spark.createDataFrame(row_results)
        results_df = results_df.withColumn("_timestamp", current_timestamp())
        results_df.write.format(self.quarantine_format).mode("append").saveAsTable(self.dq_table_name)
        print(f" Data quality results appended to table `{self.dq_table_name}`")


    def expect(self, rules: Dict[str, str]):
        """
        A decorator to validate Spark DataFrames against data quality rules.

        Parameters
        ----------
        rules : dict[str, str]
            A dictionary where keys are human-readable rule descriptions
            and values are SQL filter expressions to validate.

            Example:
            --------
            rules = {
                "Employee ID should be greater than 2": "emp_id > 2",
                "Name should not be null": "fname IS NOT NULL"
            }

        Returns
        -------
        function
            A decorated function that returns the DataFrame with
            validation results printed for each rule.

        Usage
        -----
        @DataQuality.expect(rules)
        def load_employee_df() -> DataFrame:
            return spark.read.table("employee")

        df = load_employee_df()
        """
        from pyspark.sql import SparkSession, Row, DataFrame
        from pyspark.sql.functions import current_timestamp, expr, col
        from typing import List, Dict, Optional, Callable

        def decorator(func: Callable[..., DataFrame]) -> Callable[..., DataFrame]:
            def wrapper(*args, **kwargs) -> DataFrame:
                df: DataFrame = func(*args, **kwargs)
                total_count = df.count()
                validation_results = {}
                for description, condition in rules.items():
                    failed_count = df.filter(expr(f"NOT ({condition})")).count()
                    passed_count = total_count - failed_count
                    validation_results[description] = {
                        "rule": condition,
                        "passed": passed_count,
                        "failed": failed_count,
                        "total": total_count,
                        "status": "PASSED" if failed_count == 0 else "FAILED"
                    }


                # Print results in a framework-style report
                print("="*50)
                print(" DATA QUALITY VALIDATION REPORT ")
                print("="*50)

                dq_input = []
                for desc, result in validation_results.items():
                    print(f"Rule: {desc}")
                    print(f" - Condition: {result['rule']}")
                    print(f" - Total: {result['total']} | Passed: {result['passed']} | Failed: {result['failed']}")
                    print(f" - Status: {result['status']}")
                    print("-"*50)

                    if self.dq_table_name and self.job_name:    
                        dq_input.append(
                            {
                                 "job_run_id": self.job_run_id,
                                "job_name": self.job_name,
                                "expectation_type": 'expect',
                                "rule": desc,
                                "condition": result['rule'],
                                "total_records": result['total'],
                                "passed_records": result['passed'],
                                "failed_records": result['failed'],
                                "status": result['status']
                            })
                if self.dq_table_name and self.job_name:
                    self.__dq_results_to_table(dq_input)

                return df
            return wrapper
        return decorator
    

    def expect_drop(self, rules: Dict[str, str]):
        """
        A decorator to validate Spark DataFrames against data quality rules.

        Parameters
        ----------
        rules : dict[str, str]
            A dictionary where keys are human-readable rule descriptions
            and values are SQL filter expressions to validate.

            Example:
            --------
            rules = {
                "Employee ID should be greater than 2": "emp_id > 2",
                "Name should not be null": "fname IS NOT NULL"
            }

        Returns
        -------
        function
            A decorated function that returns the filtered DataFrame with
            validation results printed for each rule.

        Usage
        -----
        @DataQuality.expect_drop(rules)
        def load_employee_df() -> DataFrame:
            return spark.read.table("employee")

        df = load_employee_df()
        """
        from pyspark.sql import DataFrame
        from pyspark.sql.functions import expr
        from typing import Callable

        def decorator(func: Callable[..., DataFrame]) -> Callable[..., DataFrame]:
            def wrapper(*args, **kwargs) -> DataFrame:
                df: DataFrame = func(*args, **kwargs)
                total_count = df.count()
                validation_results = {}
                for description, condition in rules.items():
                    failed_count = df.filter(expr(f"NOT ({condition})")).count()
                    passed_count = total_count - failed_count
                    validation_results[description] = {
                        "rule": condition,
                        "passed": passed_count,
                        "failed": failed_count,
                        "total": total_count,
                        "status": "PASSED" if failed_count == 0 else "FAILED"
                    }

                # Print results in a framework-style report
                print("="*50)
                print(" DATA QUALITY VALIDATION REPORT ")
                print("="*50)

                dq_input=[]
                for desc, result in validation_results.items():
                    print(f"Rule: {desc}")
                    print(f" - Condition: {result['rule']}")
                    print(f" - Total: {result['total']} | Passed: {result['passed']} | Failed: {result['failed']}")
                    print(f" - Status: {result['status']}")
                    print("-"*50)

                    if self.dq_table_name and self.job_name:    
                        dq_input.append(
                            {
                                "job_run_id": self.job_run_id,
                                "job_name": self.job_name,
                                "expectation_type": 'expect_drop',
                                "rule": desc,
                                "condition": result['rule'],
                                "total_records": result['total'],
                                "passed_records": result['passed'],
                                "failed_records": result['failed'],
                                "status": result['status']
                            })
                if self.dq_table_name and self.job_name:
                    self.__dq_results_to_table(dq_input)

                combined_condition = " AND ".join([f"({condition})" for condition in rules.values()])
                filtered_df = df.filter(expr(f"({combined_condition})"))

                return filtered_df
            return wrapper
        return decorator


    def expect_fail(self, rules: Dict[str, str]):
        """
        A decorator to validate Spark DataFrames against data quality rules.

        Parameters
        ----------
        rules : dict[str, str]
            A dictionary where keys are human-readable rule descriptions
            and values are SQL filter expressions to validate.

            Example:
            --------
            rules = {
                "Employee ID should be greater than 2": "emp_id > 2",
                "Name should not be null": "fname IS NOT NULL"
            }


        Returns
        -------
        function
            A decorated function that returns the DataFrame with
            validation results printed for each rule if any rule not fails.

        Usage
        -----
        @DataQuality.expect_drop(rules)
        def load_employee_df() -> DataFrame:
            return spark.read.table("employee")

        df = load_employee_df()
        """
        from pyspark.sql import DataFrame
        from pyspark.sql.functions import expr
        from typing import Callable

        def decorator(func: Callable[..., DataFrame]) -> Callable[..., DataFrame]:
            def wrapper(*args, **kwargs) -> DataFrame:
                df: DataFrame = func(*args, **kwargs)
                total_count = df.count()
                validation_results = {}
                for description, condition in rules.items():
                    failed_count = df.filter(expr(f"NOT ({condition})")).count()
                    passed_count = total_count - failed_count
                    validation_results[description] = {
                        "rule": condition,
                        "passed": passed_count,
                        "failed": failed_count,
                        "total": total_count,
                        "status": "PASSED" if failed_count == 0 else "FAILED"
                    }

                # Print results in a framework-style report
                dq_input=[]
                print("="*50)
                print(" DATA QUALITY VALIDATION REPORT ")
                print("="*50)
                for desc, result in validation_results.items():
                    print(f"Rule: {desc}")
                    print(f" - Condition: {result['rule']}")
                    print(f" - Total: {result['total']} | Passed: {result['passed']} | Failed: {result['failed']}")
                    print(f" - Status: {result['status']}")
                    print("-"*50)
                    
                    if self.dq_table_name and self.job_name:
                        dq_input.append(
                            {
                                "job_run_id": self.job_run_id,
                                "job_name": self.job_name,
                                "expectation_type": 'expect_fail',
                                "rule": desc,
                                "condition": result['rule'],
                                "total_records": result['total'],
                                "passed_records": result['passed'],
                                "failed_records": result['failed'],
                                "status": result['status']
                            })
                if self.dq_table_name and self.job_name:
                    self.__dq_results_to_table(dq_input)

                combined_condition = " AND ".join([f"({condition})" for condition in rules.values()])
                
                if df.filter(expr(f"({combined_condition})")).count() != df.count():
                    raise Exception("Pipeline execution stopped!")

                return df
            return wrapper
        return decorator
    

    def expect_quarantine(
        self,
        rules: Dict[str, str],
                ):
        """
        A decorator to validate Spark DataFrames against data quality rules,
        with optional quarantine handling for failed records.

        Parameters
        ----------
        rules : dict[str, str]
            Validation rules in form {description: sql_condition}.

        Returns
        -------
        function
            A decorated function that:
              - Prints validation results.
              - Quarantines failed records (if configured).
              - Returns the DataFrame with only the **valid (passed) records**.

        Raises
        ------
        ValueError
            If both `quarantine_location` and `quarantine_table` are provided.
            If `quarantine_format` is not one of ['parquet', 'delta', 'iceberg'].

        Usage
        -----
        >>> rules = {"Employee ID > 2": "emp_id > 2"}

        # Example 1: Quarantine to path as Delta
        >>> @DataQuality.expect_quarantine(rules, quarantine_location="/mnt/quarantine/employees", quarantine_format="delta")
        ... def load_employee_df():
        ...     return spark.read.table("employee")
        >>> df_valid = load_employee_df()

        # Example 2: Quarantine to table as Iceberg
        >>> @DataQuality.expect_quarantine(rules, quarantine_table="quarantine_employees", quarantine_format="iceberg")
        ... def load_employee_df():
        ...     return spark.read.table("employee")
        >>> df_valid = load_employee_df()
        """
        from pyspark.sql import DataFrame
        from pyspark.sql.functions import expr, current_timestamp, lit
        from typing import Callable

        if self.quarantine_location and self.quarantine_table:
            raise ValueError("Provide only one of `quarantine_location` or `quarantine_table`.")

        if self.quarantine_format not in ["parquet", "delta", "iceberg"]:
            raise ValueError("`quarantine_format` must be one of ['parquet', 'delta', 'iceberg'].")

        def decorator(func: Callable[..., DataFrame]) -> Callable[..., DataFrame]:
            def wrapper(*args, **kwargs) -> DataFrame:
                df: DataFrame = func(*args, **kwargs)
                total_count = df.count()
                valid_df = df
                # Print results in a framework-style report
                dq_input=[]
                print("="*50)
                print(" DATA QUALITY VALIDATION REPORT ")
                print("="*50)
                for desc, condition in rules.items():
                    failed_df = valid_df.filter(expr(f"NOT ({condition})"))
                    passed_df = valid_df.filter(expr(condition))

                    failed_count = failed_df.count()
                    passed_count = passed_df.count()

                    print(f"Rule: {desc}")
                    print(f" - Condition: {condition}")
                    print(f" - Total: {total_count} | Passed: {passed_count} | Failed: {failed_count}")
                    print(f" - Status: {'PASSED' if failed_count == 0 else 'FAILED'}")
                    print("-"*50)
                    
                    if self.dq_table_name and self.job_name:
                        dq_input.append(
                            {
                                "job_run_id": self.job_run_id,
                                "job_name": self.job_name,
                                "expectation_type": 'expect_quarentine',
                                "rule": desc,
                                "condition": condition,
                                "total_records": total_count,
                                "passed_records":passed_count,
                                "failed_records": failed_count,
                                "status": 'PASSED' if failed_count == 0 else 'FAILED'
                            })
                
                    # quarantine failed records if configured
                    if failed_count > 0:

                        # Add quarantine metadata
                        failed_df = (
                            failed_df
                            .withColumn("_quarantine_reason", lit(desc))
                            .withColumn("_quarantine_ts", current_timestamp())
                        )

                        if self.quarantine_location:
                            failed_df.write.option("mergeSchema", "true").format(self.quarantine_format).mode("append").save(self.quarantine_location)
                            print(f"Quarantined {failed_count} records to path: {self.quarantine_location} ({self.quarantine_format})")
                            print("-"*50)

                        if self.quarantine_table:
                            failed_df.write.option("mergeSchema", "true").format(self.quarantine_format).mode("append").saveAsTable(self.quarantine_table)
                            print(f"Quarantined {failed_count} records to table: {self.quarantine_table} ({self.quarantine_format})")
                            print("-"*50)

                    # continue only with passed records
                    valid_df = passed_df
                if self.dq_table_name and self.job_name:
                    self.__dq_results_to_table(dq_input)
                    
                return valid_df
            return wrapper
        return decorator
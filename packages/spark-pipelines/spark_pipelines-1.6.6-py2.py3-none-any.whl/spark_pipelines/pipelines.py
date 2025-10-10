        
class Pipelines:

    from pyspark.sql import SparkSession, DataFrame
    from typing import List, Dict, Optional, Callable
    
    def __init__(
        self, 
        spark: SparkSession,
        checkpoint_location: Optional[str]= None
            ):
        self.spark = spark
        self.checkpoint_location = checkpoint_location

    def table_exist(self, table_name):
        schema_df= True
        try:
            schema_df = self.spark.sql(f"DESCRIBE `{table_name}`").collect()
        except:
            schema_df= False
        return schema_df
 
    def __to_table(
        self,
        df: DataFrame,
        name: Optional[str] = None,
        path: Optional[str] = None,
        partition_cols: Optional[List[str]]= None,
        func_name: Optional[str]= None,
        table_format: str = "parquet"
            ):
        if partition_cols:
            df.write \
              .format("parquet") \
              .mode("append") \
              .partitionBy(partition_cols) \
              .saveAsTable(name)
        else:
            df.write \
              .format("parquet") \
              .mode("append") \
              .saveAsTable(name)

    def table(
        self,
        name: Optional[str] = None,
        path: Optional[str] = None,
        partition_cols: Optional[List[str]]= None,
        table_format: str = "parquet" 
            ):
        
        from pyspark.sql import DataFrame
        from typing import Callable
        
        def decorator(func: Callable[..., DataFrame]) -> Callable[..., DataFrame]:
            def wrapper(*args, **kwargs) -> DataFrame:
                df: DataFrame = func(*args, **kwargs)
                if table_format == "iceberg":
                    df.createOrReplaceTempView("iceberg_tbl_temp_vw")
                    self.spark.sql(f"INSERT INTO {name} SELECT * FROM `iceberg_tbl_temp_vw`")

                if table_format =="parquet":
                    self.__to_table(
                        df= df,
                        name=name,
                        path=path,
                        partition_cols=partition_cols,
                        func_name=func.__name__,
                        table_format=table_format)
                    
                return df
            return wrapper
        return decorator

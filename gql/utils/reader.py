# from pyspark.sql import SparkSession
# from pyspark.sql.dataframe import DataFrame
from azure.storage.blob import BlobServiceClient
import polars as pl
from io import BytesIO
from gql.config import tables_names

# def read_parquet_file_to_spark_df(file_path: str) -> DataFrame:
#     """
#     Reads a CSV file and returns a Spark DataFrame.
    
#     Args:
#         file_path (str): Path to the Parquet file
        
#     Returns:
#         DataFrame: Spark DataFrame containing the CSV data
        
#     Raises:
#         FileNotFoundError: If file does not exist
#         ValueError: If file is empty
#     """
#     try:
#         # Initialize Spark session
#         spark = SparkSession.builder \
#             .appName("CSVReader") \
#             .getOrCreate()

#         # Read the CSV file into a Spark DataFrame
#         spark_df = spark.read.parquet(file_path, header=True)

#         # Verify DataFrame is not empty
#         if spark_df.rdd.isEmpty():
#             raise ValueError(f"CSV file is empty: {file_path}")

#         # Replace NaN values with None
#         spark_df = spark_df.na.fill("")

#         return spark_df

#     except Exception as e:
#         if 'spark' in locals():
#             spark.stop()
#         raise e

def read_csv_files_to_polars_df(file_path: str) -> pl.DataFrame:
    # Azure storage account credentials
    connection_string = (
        "DefaultEndpointsProtocol=https;"
        "AccountName=mavdatalabdevsa;"
        "AccountKey=GJjIbQW7QiwpWSUwyFuFN+v7p/o7ZMSM7Yt/UKXcd6IELOMkFipstnptesHlJTSc0dR9nN2fqngT+AStVk0I/A==;"
        "EndpointSuffix=core.windows.net"
    )
    container_name = "external"
   
    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Ensure the file_path ends with a slash
    if not file_path.endswith("/"):
        file_path += "/"
    blobs = container_client.list_blobs(name_starts_with=file_path)
    # Read all CSV files into a single Polars DataFrame
    df_list = []
    for blob in blobs:
        if blob.name.endswith(".csv"):
            print(f"Reading CSV file: {blob.name}")
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().readall()
            df = pl.read_csv(BytesIO(blob_data))
            df_list.append(df)

    # Concatenate all Polars DataFrames
    if df_list:
        final_df = pl.concat(df_list, how="vertical_relaxed")
        return final_df
    else:
        return pl.DataFrame()

# def read_csv_file_to_spark_df(file_path: str) -> DataFrame:
#     """
#     Reads a CSV file and returns a Spark DataFrame.
    
#     Args:
#         file_path (str): Path to the CSV file
        
#     Returns:
#         DataFrame: Spark DataFrame containing the CSV data
        
#     Raises:
#         FileNotFoundError: If file does not exist
#         ValueError: If file is empty
#     """
#     try:
#         storage_key="GJjIbQW7QiwpWSUwyFuFN+v7p/o7ZMSM7Yt/UKXcd6IELOMkFipstnptesHlJTSc0dR9nN2fqngT+AStVk0I/A=="
#         # Initialize Spark session
#         # Initialize Spark session with proper Azure configuration
#         spark = SparkSession.builder \
#             .appName("CSVReader") \
#             .config("spark.jars.packages",
#                 ",".join([
#                     "org.apache.hadoop:hadoop-azure:3.4.1",
#                     "org.apache.hadoop:hadoop-common:3.4.1",
#                     "com.microsoft.azure:azure-storage:8.6.6",
#                     "org.apache.hadoop:hadoop-azure-datalake:3.4.1"
#                 ])) \
#             .config("spark.sql.adaptive.enabled", "true") \
#             .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
#             .config("fs.azure.account.key.mavdatalabdevsa.blob.core.windows.net", storage_key) \
#             .config("spark.hadoop.fs.azure.account.key.mavdatalabdevsa.blob.core.windows.net", storage_key) \
#             .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
#             .getOrCreate()
        
#         spark.conf.set("fs.azure.account.key.<storage_account>.blob.core.windows.net","<access_key>")

#         spark_df = spark.read.format("csv").option("header",True).option("inferSchema",True).load("wasbs://external@mavdatalabdevsa.blob.core.windows.net/platform_processor_catalog/gold/gold_csv/company/")
#         # Read the CSV file into a Spark DataFrame
#         # print(f"Reading CSV file from: {file_path}")
#         # spark_df = spark.read.csv(file_path, header=True)

#         # Verify DataFrame is not empty
#         if spark_df.rdd.isEmpty():
#             raise ValueError(f"CSV file is empty: {file_path}")

#         # Replace NaN values with None
#         # spark_df = spark_df.na.fill("")

#         return spark_df

#     except Exception as e:
#         if 'spark' in locals():
#             spark.stop()
#         raise e

   

# def list_csv_files_in_azure_storage(
#     container_name: str,
#     storage_account_name: str = "mavdatalabdevsa",
#     storage_account_key: str = "GJjIbQW7QiwpWSUwyFuFN+v7p/o7ZMSM7Yt/UKXcd6IELOMkFipstnptesHlJTSc0dR9nN2fqngT+AStVk0I/A=="
# ) -> list:
#     """
#     Lists all CSV files in a specified Azure Storage container.

#     Args:
#         container_name (str): Name of the Azure Storage container
#         storage_account_name (str): Name of the Azure Storage Account
#         storage_account_key (str): Key for the Azure Storage Account

#     Returns:
#         list: List of CSV file paths in the specified container
#     """
#     try:
#         # Initialize Spark session with Azure credentials
#         spark = SparkSession.builder \
#             .appName("AzureCSVFileLister") \
#             .getOrCreate()

#         spark.conf.set(
#             f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net",
#             storage_account_key
#         )

#         # List all files in the specified container
#         files = spark._jvm.org.apache.hadoop.fs.FileSystem.get(
#             spark._jsc.hadoopConfiguration()
#         ).listStatus(
#             spark._jvm.org.apache.hadoop.fs.Path(f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net/")
#         )

#         # Filter and return only CSV files
#         csv_files = [file.getPath().toString() for file in files if file.getPath().getName().endswith('.csv')]

#         return csv_files

#     except Exception as e:
#         if 'spark' in locals():
#             spark.stop()
#         raise e
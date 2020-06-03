from pyspark.sql import SparkSession


def init_spark():
    """This function is used to initialize Spark Session and Context"""
    spark = SparkSession.builder.appName("PROJECT").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")  # Set logLevel to ERROR
    return spark, sc


def load_csv_data(spark, file_path):
    """
    This function is used to load csv files

    :param spark: spark session
    :return: csv file
    """
    data = spark.read.csv(file_path, header=True, inferSchema=True)
    return data

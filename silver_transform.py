from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, hour as spark_hour
from pyspark.sql.types import LongType, TimestampType


BRONZE_PATH = "lakehouse/bronze/clickstream"
SILVER_PATH = "lakehouse/silver/clickstream_cleansed"


def build_spark_session():
    return SparkSession.builder.appName("NexusFlow-Silver-Transformation").getOrCreate()


def main():
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("ERROR")

    print("[INFO] Starting Silver transformation...")

    try:
        bronze_df = spark.read.parquet(BRONZE_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to read bronze data from {BRONZE_PATH}: {e}")
        spark.stop()
        return

    print(f"[INFO] Loaded bronze data from {BRONZE_PATH}")

    if bronze_df.rdd.isEmpty():
        print("[INFO] No records found in bronze data. Exiting gracefully.")
        spark.stop()
        return

    print("[INFO] Cleaning and enriching data...")

    cleaned_df = (
        bronze_df.dropDuplicates(["event_id", "timestamp"])
        .withColumn("timestamp", col("timestamp").cast(TimestampType()))
        .withColumn("user_id", col("user_id").cast(LongType()))
        .withColumn("date", date_format(col("timestamp"), "yyyy-MM-dd"))
        .withColumn("hour", spark_hour(col("timestamp")).cast("int"))
    )

    print("[INFO] Writing silver data to parquet...")
    (
        cleaned_df.write.mode("overwrite")
        .partitionBy("date")
        .parquet(SILVER_PATH)
    )

    print(f"[SUCCESS] Silver data written to {SILVER_PATH}")
    spark.stop()


if __name__ == "__main__":
    main()

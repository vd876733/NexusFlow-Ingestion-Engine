from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, countDistinct


SILVER_PATH = "lakehouse/silver/clickstream_cleansed"
GOLD_PATH = "lakehouse/gold/hourly_user_engagement"


def build_spark_session():
    return SparkSession.builder.appName("NexusFlow-Gold-Aggregations").getOrCreate()


def main():
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("ERROR")

    print("[INFO] Starting Gold aggregation pipeline...")

    try:
        silver_df = spark.read.parquet(SILVER_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to read silver data from {SILVER_PATH}: {e}")
        spark.stop()
        return

    print(f"[INFO] Loaded silver data from {SILVER_PATH}")

    if silver_df.rdd.isEmpty():
        print("[WARNING] No records found in silver data. Exiting gracefully.")
        spark.stop()
        return

    print("[INFO] Aggregating metrics by date, hour, and event_type...")

    gold_df = (
        silver_df.groupBy("date", "hour", "event_type")
        .agg(
            count(col("event_id")).alias("total_events"),
            countDistinct(col("user_id")).alias("unique_users"),
        )
        .orderBy("date", "hour", "event_type")
    )

    print("[INFO] Writing Gold metrics to parquet...")
    gold_df.write.mode("overwrite").parquet(GOLD_PATH)

    print(f"[SUCCESS] Gold metrics written to {GOLD_PATH}")
    spark.stop()


if __name__ == "__main__":
    main()

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit


CLEAN_PATH = "lakehouse/bronze/clickstream"
DLQ_PATH = "lakehouse/bronze/dlq"


def build_spark_session():
    return SparkSession.builder.appName("VerifyLakehouse").getOrCreate()


def print_dataset_summary(spark, path, label, format_name):
    print(f"\n=== {label} ===")
    try:
        df = spark.read.format(format_name).load(path) if format_name != "json" else spark.read.json(path)
        count = df.count()
        print(f"Total rows: {count}")

        if count > 0:
            print("\nTop 5 records:")
            df.show(5, truncate=False)

            if "event_type" in df.columns:
                dist_df = (
                    df.groupBy("event_type")
                    .count()
                    .withColumn("percentage", (col("count") / lit(count) * 100).cast("double"))
                    .orderBy("event_type")
                )
                print("\nEvent type distribution:")
                dist_df.show(truncate=False)
            else:
                print("\nNo event_type column found for distribution analysis.")
        else:
            print("No records found.")
    except Exception as e:
        print(f"Could not read {label.lower()} data from {path}: {e}")


def main():
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("\n=== Lakehouse Verification ===")
    print_dataset_summary(spark, CLEAN_PATH, "Clean Clickstream Data", "parquet")
    print_dataset_summary(spark, DLQ_PATH, "Dead-Letter Queue Data", "json")

    spark.stop()


if __name__ == "__main__":
    main()

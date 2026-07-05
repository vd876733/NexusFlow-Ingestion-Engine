import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, LongType

def main():
    # 1. Initialize a pure Spark Session (No Delta configurations required)
    spark = SparkSession.builder \
        .appName("NexusFlow-Ingestion-Stream") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    print("⚡ NexusFlow Spark Streaming Engine initialized...")

    # 2. Define strict schema matching our producer payload
    clickstream_schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("user_id", LongType(), True),
        StructField("event_type", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("ip_address", StringType(), True)
    ])

    # 3. Read stream from Kafka (using internal container mapping)
    kafka_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9093") \
        .option("subscribe", "web-clickstream") \
        .option("startingOffsets", "latest") \
        .load()

    # 4. Cast payload from binary to string and parse JSON fields
    parsed_stream = kafka_stream \
        .selectExpr("CAST(value AS STRING) as json_payload") \
        .select(from_json(col("json_payload"), clickstream_schema).alias("data")) \
        .select("data.*")

    # 5. Filter streams
    dlq_stream = parsed_stream.filter(col("user_id").isNull())
    clean_stream = parsed_stream.filter(col("user_id").isNotNull())

    print("📡 Pipeline routing maps established. Activating sinks...")

    # 6. Write DLQ anomalies to local storage as JSON format
    dlq_query = dlq_stream.writeStream \
        .format("json") \
        .option("path", "lakehouse/bronze/dlq") \
        .option("checkpointLocation", "lakehouse/checkpoints/dlq") \
        .outputMode("append") \
        .start()

    # 7. Write Valid records to local Bronze layer using native Parquet format
    clean_query = clean_stream.writeStream \
        .format("parquet") \
        .option("path", "lakehouse/bronze/clickstream") \
        .option("checkpointLocation", "lakehouse/checkpoints/clickstream") \
        .outputMode("append") \
        .start()

    # Keep streaming loops alive
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()
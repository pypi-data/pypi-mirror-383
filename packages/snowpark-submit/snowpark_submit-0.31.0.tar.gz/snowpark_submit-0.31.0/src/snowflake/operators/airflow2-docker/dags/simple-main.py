import logging

from pyspark.sql import Row, SparkSession

logger = logging.getLogger("snowflake_connect_server")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [Thread %(thread)d] - %(message)s"
)
console_handler.setFormatter(formatter)

# Display the logs to the console
logger.addHandler(console_handler)

def test_body(spark):
    spark.createDataFrame(
        [
            Row(a=1, b=2.0),
            Row(a=2, b=3.0),
            Row(a=4, b=5.0),
        ]
    ).show() 


if __name__ == "__main__":
    logger.info("pyspark client app running...")
    spark = SparkSession.builder.getOrCreate()
    test_body(spark)
    logger.info("pyspark job finished.")
    spark.stop()

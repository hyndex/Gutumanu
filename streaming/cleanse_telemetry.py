from __future__ import annotations

"""Flink job to cleanse telemetry records.

This job reads raw telemetry data, replaces any ``NaN`` numeric values with
``NULL`` and writes the cleaned records to the ``telemetry.clean`` sink.

Watermarks are generated with a five second out-of-order allowance and
late events older than thirty seconds beyond the watermark are dropped.
"""

import math
from datetime import datetime, timedelta

from pyflink.common import Types, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink
from pyflink.datastream.formats.json import JsonRowDeserializationSchema, JsonRowSerializationSchema


RAW_TOPIC = "telemetry.raw"
CLEAN_TOPIC = "telemetry.clean"
WATERMARK_LAG_MS = 5000
LATE_EVENT_THRESHOLD_SEC = 30


def cleanse(record: dict) -> dict:
    """Replace ``NaN`` values with ``None`` in a telemetry record."""
    cleansed = {}
    for key, value in record.items():
        if isinstance(value, float) and math.isnan(value):
            cleansed[key] = None
        else:
            cleansed[key] = value
    return cleansed


def main() -> None:
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(60_000)

    ds_schema = JsonRowDeserializationSchema.builder()\
        .type_info(
            Types.ROW([
                Types.STRING(),  # device_id
                Types.DOUBLE(),  # energy_rate
                Types.FLOAT(),   # latitude
                Types.FLOAT(),   # longitude
                Types.SQL_TIMESTAMP()  # event_time
            ])
        )\
        .build()

    src = KafkaSource.builder()\
        .set_bootstrap_servers("kafka:9092")\
        .set_topics(RAW_TOPIC)\
        .set_group_id("telemetry-cleanse")\
        .set_value_only_deserializer(ds_schema)\
        .build()

    sink_schema = JsonRowSerializationSchema.builder()\
        .with_type_info(Types.MAP(Types.STRING(), Types.STRING()))\
        .build()

    sink = KafkaSink.builder()\
        .set_bootstrap_servers("kafka:9092")\
        .set_record_serializer(sink_schema)\
        .set_topic(CLEAN_TOPIC)\
        .build()

    watermark_strategy = WatermarkStrategy\
        .for_bounded_out_of_orderness(timedelta(milliseconds=WATERMARK_LAG_MS))\
        .with_timestamp_assigner(lambda record, ts: int(record[4].timestamp() * 1000))

    stream = env.from_source(src, watermark_strategy, "telemetry-source")

    cleaned = stream.map(lambda r: cleanse({
        "device_id": r[0],
        "energy_rate": r[1],
        "lat": r[2],
        "lon": r[3],
        "event_time": r[4]
    }), Types.MAP(Types.STRING(), Types.STRING()))

    cleaned.sink_to(sink)

    env.execute("telemetry-cleanse")


if __name__ == "__main__":
    main()

from __future__ import annotations

"""Z-score anomaly detection on energy_rate with rolling windows."""

import statistics
from datetime import timedelta
from typing import Dict

from pyflink.common import Types, WatermarkStrategy
from pyflink.datastream import (ProcessWindowFunction,
                                StreamExecutionEnvironment, Time)
from pyflink.datastream.connectors.kafka import KafkaSink, KafkaSource
from pyflink.datastream.formats.json import (JsonRowDeserializationSchema,
                                             JsonRowSerializationSchema)
from pyflink.datastream.window import SlidingEventTimeWindows


CLEAN_TOPIC = "telemetry.clean"
ANOMALY_TOPIC = "anomaly"
WATERMARK_LAG_MS = 5000
LATE_EVENT_THRESHOLD_SEC = 30
Z_THRESHOLD = 3.0
WINDOW_SIZE_MIN = 5
WINDOW_SLIDE_MIN = 1


class ZScoreWindow(ProcessWindowFunction):
    def process(self, key, context, elements, out):
        values = [float(e["energy_rate"]) for e in elements]
        mean = statistics.fmean(values)
        stdev = statistics.pstdev(values)
        for e in elements:
            z = (float(e["energy_rate"]) - mean) / stdev if stdev else 0.0
            if abs(z) > Z_THRESHOLD:
                out.collect({
                    "device_id": e["device_id"],
                    "z_score": z,
                    "energy_rate": e["energy_rate"],
                    "event_time": e["event_time"]
                })


def main() -> None:
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(60_000)

    ds_schema = JsonRowDeserializationSchema.builder()\
        .type_info(Types.MAP(Types.STRING(), Types.STRING()))\
        .build()

    src = KafkaSource.builder()\
        .set_bootstrap_servers("kafka:9092")\
        .set_topics(CLEAN_TOPIC)\
        .set_group_id("energy-anomaly")\
        .set_value_only_deserializer(ds_schema)\
        .build()

    sink_schema = JsonRowSerializationSchema.builder()\
        .with_type_info(Types.MAP(Types.STRING(), Types.STRING()))\
        .build()

    sink = KafkaSink.builder()\
        .set_bootstrap_servers("kafka:9092")\
        .set_record_serializer(sink_schema)\
        .set_topic(ANOMALY_TOPIC)\
        .build()

    watermark_strategy = WatermarkStrategy\
        .for_bounded_out_of_orderness(timedelta(milliseconds=WATERMARK_LAG_MS))\
        .with_timestamp_assigner(lambda record, ts: int(record["event_time"].timestamp() * 1000))

    stream = env.from_source(src, watermark_strategy, "clean-telemetry")

    windows = stream.key_by(lambda r: r["device_id"], key_type=Types.STRING())\
        .window(SlidingEventTimeWindows.of(Time.minutes(WINDOW_SIZE_MIN), Time.minutes(WINDOW_SLIDE_MIN)))\
        .allowed_lateness(Time.seconds(LATE_EVENT_THRESHOLD_SEC))\
        .process(ZScoreWindow(), Types.MAP(Types.STRING(), Types.STRING()))

    windows.sink_to(sink)

    env.execute("energy-anomaly")


if __name__ == "__main__":
    main()

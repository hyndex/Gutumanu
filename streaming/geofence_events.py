from __future__ import annotations

"""Detect geofence enter/exit events from cleansed telemetry."""

from dataclasses import dataclass
from datetime import timedelta
from typing import Dict

from pyflink.common import Types, WatermarkStrategy
from pyflink.datastream import (ProcessFunction,
                                RuntimeContext, StreamExecutionEnvironment)
from pyflink.datastream.connectors.kafka import KafkaSink, KafkaSource
from pyflink.datastream.formats.json import (JsonRowDeserializationSchema,
                                             JsonRowSerializationSchema)
from pyflink.datastream.state import ValueStateDescriptor


CLEAN_TOPIC = "telemetry.clean"
EVENT_TOPIC = "event"
WATERMARK_LAG_MS = 5000
LATE_EVENT_THRESHOLD_SEC = 30


@dataclass
class Geofence:
    name: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float

    def contains(self, lat: float, lon: float) -> bool:
        return self.min_lat <= lat <= self.max_lat and self.min_lon <= lon <= self.max_lon


GEOFENCES = [
    Geofence("office", 40.0, 41.0, -74.0, -73.0),
    Geofence("school", 35.0, 36.0, -80.0, -79.0),
]


class DeviceGeofenceProcess(ProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("current_zone", Types.STRING())
        self.current_zone = runtime_context.get_state(descriptor)

    def process_element(self, value: Dict, ctx: ProcessFunction.Context, out: ProcessFunction.Collector):
        lat = value["lat"]
        lon = value["lon"]
        device_id = value["device_id"]
        ts = value["event_time"]
        current = self.current_zone.value()
        zone = next((g.name for g in GEOFENCES if g.contains(lat, lon)), None)
        if zone != current:
            event_type = "enter" if zone and not current else "exit"
            self.current_zone.update(zone)
            out.collect({
                "device_id": device_id,
                "event_type": event_type,
                "zone": zone or current,
                "event_time": ts
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
        .set_group_id("geofence-events")\
        .set_value_only_deserializer(ds_schema)\
        .build()

    sink_schema = JsonRowSerializationSchema.builder()\
        .with_type_info(Types.MAP(Types.STRING(), Types.STRING()))\
        .build()

    sink = KafkaSink.builder()\
        .set_bootstrap_servers("kafka:9092")\
        .set_record_serializer(sink_schema)\
        .set_topic(EVENT_TOPIC)\
        .build()

    watermark_strategy = WatermarkStrategy\
        .for_bounded_out_of_orderness(timedelta(milliseconds=WATERMARK_LAG_MS))\
        .with_timestamp_assigner(lambda record, ts: int(record["event_time"].timestamp() * 1000))

    stream = env.from_source(src, watermark_strategy, "clean-telemetry")

    events = stream.process(DeviceGeofenceProcess(), Types.MAP(Types.STRING(), Types.STRING()))

    events.sink_to(sink)

    env.execute("geofence-events")


if __name__ == "__main__":
    main()

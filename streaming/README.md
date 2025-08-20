# Streaming Jobs

This module contains PyFlink jobs used for telemetry processing and analytics.

## Jobs

### `cleanse_telemetry.py`
Cleanses incoming telemetry by converting `NaN` numeric values to `NULL` and
writes the result to the `telemetry.clean` topic.

### `geofence_events.py`
Consumes cleansed telemetry and emits `enter`/`exit` events when devices cross
predefined geofences, writing to the `event` topic.

### `energy_anomaly.py`
Performs z-score based anomaly detection on the `energy_rate` field using a
five-minute rolling window. Anomalies are written to the `anomaly` topic.

Each job assigns event-time watermarks with a five second bound on
out-of-order data and drops events arriving more than thirty seconds
late.

## Deployment

The `deploy/` directory contains a sample Kubernetes `StatefulSet` for running
the jobs with checkpointing enabled.

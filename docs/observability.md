# SLO Dashboards

The monitoring stack exposes Prometheus metrics for all services. Example dashboards:

* **Request latency**: `histogram_quantile` over `http_server_requests_seconds_bucket` to track FastAPI and Django latencies.
* **Kafka throughput**: `kafka_*_published_total` counters.
* **Database writes**: `ingest_db_writes_total` gauge.
* **Django/Postgres metrics**: exposed via `/metrics` endpoint from `django-prometheus`.

Use Grafana connected to Prometheus to chart these metrics and define SLOs such as 99th percentile latency and error rates.

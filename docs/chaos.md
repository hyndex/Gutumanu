# Chaos Testing

The `chaos` scripts intentionally kill services or introduce latency to validate resilience and alerting.

Example experiments:

1. **Terminate Kafka broker**: ensure producers handle failures and alerts fire.
2. **Add latency to Postgres** using `tc` to verify SLO violation detection.
3. **Crash FastAPI service** instances via `kill -9` to test auto-recovery.

Run these scripts in staging and monitor dashboards to confirm SLOs and alerts.

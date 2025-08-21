from django.db import migrations

CREATE_CANONICAL_SQL = """
-- Organization table
CREATE TABLE IF NOT EXISTS organization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL
);
ALTER TABLE organization ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON organization
    USING (id = current_setting('app.current_organization', true)::uuid);

-- Principal table
CREATE TABLE IF NOT EXISTS principal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    data JSONB
);
ALTER TABLE principal ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON principal
    USING (organization_id = current_setting('app.current_organization', true)::uuid);

-- Device table
CREATE TABLE IF NOT EXISTS device (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    principal_id UUID REFERENCES principal(id) ON DELETE SET NULL,
    serial_number TEXT,
    data JSONB
);
ALTER TABLE device ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON device
    USING (organization_id = current_setting('app.current_organization', true)::uuid);

-- Telemetry table partitioned by time and organization
CREATE TABLE IF NOT EXISTS telemetry (
    time TIMESTAMPTZ NOT NULL,
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    device_id UUID REFERENCES device(id) ON DELETE SET NULL,
    data JSONB,
    location GEOGRAPHY(Point, 4326),
    PRIMARY KEY (time, organization_id, device_id)
) PARTITION BY RANGE (time);

CREATE TABLE IF NOT EXISTS telemetry_default PARTITION OF telemetry
    FOR VALUES FROM ('2000-01-01') TO ('2100-01-01')
    PARTITION BY HASH (organization_id);
CREATE TABLE IF NOT EXISTS telemetry_default_p0 PARTITION OF telemetry_default
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE IF NOT EXISTS telemetry_default_p1 PARTITION OF telemetry_default
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE IF NOT EXISTS telemetry_default_p2 PARTITION OF telemetry_default
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE IF NOT EXISTS telemetry_default_p3 PARTITION OF telemetry_default
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

CREATE INDEX IF NOT EXISTS telemetry_data_gin_idx ON telemetry USING GIN (data);
CREATE INDEX IF NOT EXISTS telemetry_location_gist_idx ON telemetry USING GIST (location);

ALTER TABLE telemetry ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON telemetry
    USING (organization_id = current_setting('app.current_organization', true)::uuid);

-- Event table
CREATE TABLE IF NOT EXISTS event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    telemetry_time TIMESTAMPTZ REFERENCES telemetry(time),
    device_id UUID REFERENCES device(id) ON DELETE SET NULL,
    type TEXT NOT NULL,
    data JSONB
);
ALTER TABLE event ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON event
    USING (organization_id = current_setting('app.current_organization', true)::uuid);

-- Anomaly table
CREATE TABLE IF NOT EXISTS anomaly (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    event_id UUID REFERENCES event(id) ON DELETE SET NULL,
    score NUMERIC,
    data JSONB
);
ALTER TABLE anomaly ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON anomaly
    USING (organization_id = current_setting('app.current_organization', true)::uuid);

-- Alert table
CREATE TABLE IF NOT EXISTS alert (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    anomaly_id UUID REFERENCES anomaly(id) ON DELETE SET NULL,
    rule_id UUID,
    created_at TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE alert ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON alert
    USING (organization_id = current_setting('app.current_organization', true)::uuid);

-- Rule table
CREATE TABLE IF NOT EXISTS rule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    definition JSONB
);
ALTER TABLE rule ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON rule
    USING (organization_id = current_setting('app.current_organization', true)::uuid);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    principal_id UUID REFERENCES principal(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    details JSONB
);
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON audit_log
    USING (organization_id = current_setting('app.current_organization', true)::uuid);

-- TimescaleDB hypertable and continuous aggregate configuration
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable('telemetry', 'time', partitioning_column => 'organization_id', if_not_exists => TRUE);
        CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_hourly
        WITH (timescaledb.continuous) AS
            SELECT organization_id,
                   time_bucket('1 hour', time) AS bucket,
                   AVG((data->>'value')::DOUBLE PRECISION) AS avg_value
            FROM telemetry
            GROUP BY organization_id, bucket;
    END IF;
END;
$$;
"""

DROP_CANONICAL_SQL = """
DROP MATERIALIZED VIEW IF EXISTS telemetry_hourly;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS rule CASCADE;
DROP TABLE IF EXISTS alert CASCADE;
DROP TABLE IF EXISTS anomaly CASCADE;
DROP TABLE IF EXISTS event CASCADE;
DROP TABLE IF EXISTS telemetry CASCADE;
DROP TABLE IF EXISTS device CASCADE;
DROP TABLE IF EXISTS principal CASCADE;
DROP TABLE IF EXISTS organization CASCADE;
"""

class Migration(migrations.Migration):
    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=CREATE_CANONICAL_SQL,
            reverse_sql=DROP_CANONICAL_SQL,
        ),
    ]

#!/bin/bash
set -euo pipefail

CONNECT_URL=${CONNECT_URL:-http://localhost:8083}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

register() {
  local name=$1
  echo "Registering $name connector"
  curl -s -X PUT -H "Content-Type: application/json" \
    --data @"$SCRIPT_DIR/debezium/${name}.json" \
    "$CONNECT_URL/connectors/${name}/config" > /dev/null
}

register postgres-source
register iceberg-sink

echo "Connectors registered"

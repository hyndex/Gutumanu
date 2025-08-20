#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="$(dirname "$0")/certs"

docker exec redpanda rpk acl user create karapace -p karapace-secret \
  --api-urls redpanda:9644 \
  --tls-truststore "$CERT_DIR/ca.crt" \
  --tls-cert "$CERT_DIR/server.crt" \
  --tls-key "$CERT_DIR/server.key"

docker exec redpanda rpk acl create \
  --allow-principal user:karapace \
  --operation read --operation write --operation describe \
  --topic '*' \
  --api-urls redpanda:9644 \
  --tls-truststore "$CERT_DIR/ca.crt" \
  --tls-cert "$CERT_DIR/server.crt" \
  --tls-key "$CERT_DIR/server.key"

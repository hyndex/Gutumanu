#!/bin/bash
set -e

docker exec redpanda rpk acl user create producer --new-password producer-pass || true
docker exec redpanda rpk acl create --allow-principal User:producer --operation write --topic telemetry.raw --brokers redpanda:9093 --tls-enabled --user admin --password admin --tls-truststore /etc/redpanda/certs/ca.crt

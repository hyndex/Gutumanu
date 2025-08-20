#!/usr/bin/env bash
set -euo pipefail

DIR="$(dirname "$0")/certs"
mkdir -p "$DIR"

# Certificate authority
openssl genrsa -out "$DIR/ca.key" 2048
openssl req -x509 -new -nodes -key "$DIR/ca.key" -sha256 -days 3650 \
  -subj "/CN=ca" -out "$DIR/ca.crt"

# Broker certificate
openssl genrsa -out "$DIR/server.key" 2048
openssl req -new -key "$DIR/server.key" -out "$DIR/server.csr" -subj "/CN=redpanda"
openssl x509 -req -in "$DIR/server.csr" -CA "$DIR/ca.crt" -CAkey "$DIR/ca.key" \
  -CAcreateserial -out "$DIR/server.crt" -days 3650 -sha256

# Client certificate for Karapace
openssl genrsa -out "$DIR/client.key" 2048
openssl req -new -key "$DIR/client.key" -out "$DIR/client.csr" -subj "/CN=karapace"
openssl x509 -req -in "$DIR/client.csr" -CA "$DIR/ca.crt" -CAkey "$DIR/ca.key" \
  -CAcreateserial -out "$DIR/client.crt" -days 3650 -sha256

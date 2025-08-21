# Gutumanu 🚀
*The Ultimate (Under Construction) Tracking System*

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/gutumanu/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/yourusername/gutumanu/releases)

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Project Layout](#project-layout)
5. [Quick Start](#quick-start)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Running the Django Server](#running-the-django-server)
   - [Running the Ingest Service](#running-the-ingest-service)
6. [Tracking Walkthrough](#tracking-walkthrough)
   - [Device Registration and Tokens](#device-registration-and-tokens)
   - [JavaScript Client](#javascript-client)
   - [REST Endpoints](#rest-endpoints)
   - [WebSocket Alerts](#websocket-alerts)
7. [Analytics API](#analytics-api)
8. [Authentication & OIDC](#authentication--oidc)
9. [Logging & Monitoring](#logging--monitoring)
10. [Testing](#testing)
11. [Contributing](#contributing)
12. [License](#license)
13. [Disclaimer](#disclaimer)

---

## Overview
**Gutumanu** is a next‑generation, production‑ready tracking system built on Django and modern web APIs. It is designed for parents who want to keep their children safe while learning how cutting‑edge telemetry pipelines work. **Gutumanu** captures location, device, and sensor data from a browser client, ingests structured telemetry through a FastAPI microservice, and exposes rich administration and analytics interfaces. The project is under heavy construction and intended for ethical use only.

---

## Architecture
Gutumanu is composed of several parts that work together:

| Component | Technology | Purpose |
|-----------|------------|---------|
| `tracking` | Django app + JavaScript | Collects location, device, and permission data from a browser and stores it in the database. |
| `ingest_service` | FastAPI + Kafka | Accepts high‑volume telemetry and trip data via versioned APIs and streams it to Kafka after rule evaluation. |
| `analytics` | Django REST | Allows the creation and retrieval of analytics jobs that run SQL and store results in S3. |
| `authapp` | Django views | Minimal SCIM‑style user and group endpoints for identity integration. |
| `audit` | Middleware | Logs every request with optional PII scrubbing and OpenSearch export. |
| `rules` | Tiny rule engine | Parses YAML rules and executes actions against ingest payloads. |
| `GutumanuMobile` | React Native (prototype) | Placeholder mobile app and tests for future native capabilities. |

The default database is SQLite for development, and Redis is used for Channels websockets. Kafka is required for the ingest service if streaming is enabled.

---

## Features
### Core Tracking
- **Real‑Time Location** – latitude, longitude and accuracy stored as `LocationLog` records.
- **IP Logging** – captures IP address and network details (`IPLog`).
- **Device Information** – user‑agent, platform and screen size (`DeviceInfoLog`).
- **Photo Capture** – optional webcam snapshot with coordinates (`PhotoCapture`).
- **Sensor Data** – accelerometer, gyroscope and other sensor readings (`SensorDataLog`).
- **Permission Auditing** – tracks which browser permissions are granted (`PermissionLog`).
- **SMS/Call/Social Logs** – optional logs for SMS messages, phone calls and social media messages.
- **App Usage & Screen Time** – foreground usage for apps and daily totals.
- **Geofencing** – entry/exit events with radius and optional stealth mode (`GeofenceAlert`).
- **Keylogger (demo)** – records keystrokes to illustrate security boundaries.

### Telemetry & Analytics
- **Versioned Ingestion API** (`/telemetry`, `/trip`) with rate limiting and idempotency keys.
- **Kafka Streaming** – accepted payloads are published to a Kafka topic via `KafkaSink`.
- **Rule Engine** – YAML rules evaluate ingest payloads and can trigger actions.
- **Analytics Jobs** – submit SQL jobs and fetch results for offline analysis.

### Administration & Monitoring
- **Django Admin** – manage children, logs, alerts and AI jobs with inlines and map links.
- **WebSocket Alerts** – real‑time alert streaming via Channels consumers.
- **Prometheus Metrics** – middleware emits metrics for both Django and FastAPI services.
- **Structured Logging** – JSON logs with PII scrubbing and optional OpenSearch handler.

---

## Project Layout
```
Gutumanu/
├── authapp/              # SCIM user/group endpoints
├── analytics/            # Analytics job API
├── ingest_service/       # FastAPI ingest microservice
├── tracking/             # Browser tracking app
├── rules/                # YAML rule engine
├── audit/                # Request logging middleware
├── GutumanuMobile/       # Prototype mobile app
├── manage.py             # Django management entry point
└── requirements.txt      # Base Python dependencies
```

---

## Quick Start
### Prerequisites
- **Python 3.8+** (virtual environment strongly recommended)
- **Node.js & npm** (only for building the optional mobile app)
- **Redis** running on `localhost:6379` for websocket support
- **Kafka broker** (for the ingest service)

Optional libraries required at runtime:
`djangorestframework`, `channels`, `mozilla-django-oidc`, `django-prometheus`, `python-json-logger`, `Pillow`, `PyYAML`.

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/gutumanu.git
   cd gutumanu
   ```
2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install djangorestframework channels django-prometheus mozilla-django-oidc \
               python-json-logger Pillow PyYAML
   ```
4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```
5. **Create an admin user**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Django Server
```bash
python manage.py runserver
```
Visit <http://localhost:8000/admin/> to access the admin interface and <http://localhost:8000/tracking/placeholder/> from the device you wish to track. The first visit asks for permissions and generates a device ID stored in local storage.

### Running the Ingest Service
The ingest service accepts high‑volume telemetry independently of the Django app.
```bash
uvicorn ingest_service.main:app --reload
```
Environment variables:
- `RATE_LIMIT_RATE` and `RATE_LIMIT_CAPACITY` – token bucket configuration.
- `OTEL_EXPORTER_OTLP_ENDPOINT` – enable OpenTelemetry export.
- Kafka configuration is read from `kafka.py` (defaults to localhost).

Example telemetry ingestion:
```bash
curl -X POST http://localhost:8000/telemetry \
  -H 'Content-Type: application/vnd.telemetry.v1+json' \
  -H 'Idempotency-Key: 123' -H 'Org-Id: demo' \
  -d '{"device_id":"child-1","latitude":1.23,"longitude":4.56}'
```
A successful request returns `{"status": "accepted"}`.

---

## Tracking Walkthrough
### Device Registration and Tokens
1. **Create a `Child` record** in the Django admin with a unique `device_id` and parent user.
2. **Generate an auth token** via `POST /tracking/token-renew/`:
   ```bash
   curl -X POST http://localhost:8000/tracking/token-renew/ \
     -H 'Content-Type: application/json' \
     -d '{"device_id": "child-1"}'
   # → {"new_token": "..."}
   ```
3. The browser client stores this token and includes it in the `X-Auth-Token` header for future requests along with `X-Device-ID`.

### JavaScript Client
`tracking/static/tracking/js/tracking.js` automatically:
- Generates/stores a device ID.
- Requests permissions (geolocation, camera, sensors, notifications).
- Sends periodic updates to the endpoints below.
- Checks `/tracking/api/js_version/` for updates and reloads if required.
- Respects per‑device update intervals from `/tracking/api/get_update_interval/`.

### REST Endpoints
All endpoints live under `/tracking/api/` and accept JSON unless noted. Example payloads show the minimum fields; additional metadata is allowed.

| Endpoint | Payload (JSON) | Description |
|----------|----------------|-------------|
| `POST /location/` | `{device_id, latitude, longitude, accuracy}` | Store GPS coordinates. |
| `POST /ip/` | `{device_id, ip_address, details}` | Log the public IP address. |
| `POST /device/` | `{device_id, user_agent, platform, screen_width, screen_height}` | Save device/browser info. |
| `POST /photo/` | multipart form with `image` plus optional `latitude` & `longitude` | Upload a webcam snapshot. |
| `POST /sensor/` | `{device_id, data:{...}}` | Save arbitrary sensor readings. |
| `POST /permission/` | `{device_id, geolocation, camera, ...}` | Record granted/denied permissions. |
| `POST /sms/` | `{device_id, message, sender, receiver, direction}` | Log an SMS message. |
| `POST /call/` | `{device_id, number, duration, type}` | Log a call. |
| `POST /social/` | `{device_id, platform, content, sender}` | Record a social‑media message. |
| `POST /keylogger/` | `{device_id, keystrokes}` | (Demo) keystroke log. |

All endpoints respond with `{"status": "ok"}` on success or `400` with an error message.

### WebSocket Alerts
Alerts are delivered over websockets at `ws://<host>/ws/alerts/`.

Example client:
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/alerts/?token=resume-token');
socket.onmessage = ev => console.log('alert', ev.data);
socket.onopen = () => socket.send(JSON.stringify({type: 'heartbeat'}));
```
Messages follow a JSON structure: `{type: 'alert', data: {...}, token: 'resume-token'}`.

---

## Analytics API
Create an analytics job by posting SQL and fetch its status later.
```bash
# Create
curl -X POST http://localhost:8000/analytics/jobs/ \
  -H 'Content-Type: application/json' \
  -d '{"sql_query": "SELECT 1"}'
# → {"id": "<uuid>"}

# Retrieve
curl http://localhost:8000/analytics/jobs/<uuid>/
```
The detail response includes the stored `result_s3_uri` and job `status`.

---

## Authentication & OIDC
Gutumanu supports OpenID Connect via `mozilla_django_oidc`.
Set the following environment variables to enable it:
- `OIDC_RP_CLIENT_ID`
- `OIDC_RP_CLIENT_SECRET`
- `OIDC_OP_AUTHORIZATION_ENDPOINT`
- `OIDC_OP_TOKEN_ENDPOINT`
- `OIDC_OP_USER_ENDPOINT`

Fallback authentication uses Django’s default model backend. Basic SCIM endpoints are available under `/auth/` for user/group provisioning.

---

## Logging & Monitoring
- **Structured JSON logs** are emitted by default; PII fields are filtered by `PIIFilter`.
- **Prometheus metrics** are exposed at `/metrics` for Django and via the FastAPI instrumentator.
- **OpenSearchHandler** can ship logs to an OpenSearch cluster if configured in `settings.py`.

---

## Testing
Run the full test suite:
```bash
python manage.py test
```
This executes Django tests as well as the FastAPI ingest service unit tests.

---

## Contributing
We welcome feature suggestions, bug reports and pull requests. Fork the repository, make your changes and submit a PR. Please ensure contributions respect privacy and legal boundaries.

---

## License
This project is open‑source under the [MIT License](LICENSE).

---

## Disclaimer
Gutumanu is provided for educational and **ethical** use only. Always obtain consent before tracking any individual. Misuse of this project for spying or unlawful surveillance is strictly forbidden.

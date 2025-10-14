# Depths

Everything you need to build your observability stack — unified, OTel-compatible, S3-native telemetry. Built by **Depths AI**.

Depths collects traces, logs, and metrics over OTLP HTTP, writes them into Delta Lake tables by UTC day, and can ship sealed days to S3. You also get minute-wise stats snapshots, a real-time stream, a tiny query API, and a clean Python surface for ingest and reads.

Docs live at **[https://docs.depthsai.com](https://docs.depthsai.com)**.

---

## Why Depths

* **OTel first** – accept standard OTLP JSON today, add protobuf by installing an extra
* **Delta Lake by default** – predictable schema across six OTel tables
* **S3 native** – seal a past UTC day, upload, verify rowcounts, then clean local state
* **Polars inside** – fast typed DataFrames and LazyFrames for compact reads
* **Real-time + rollups** – in-memory tail (SSE) and minute-wise stats in a local Delta
* **Simple to start** – `depths init` then `depths start`

---

## Install

```bash
# core (JSON ingest)
pip install depths

# optional protobuf ingest (OTLP x-protobuf)
pip install "depths[proto]"
```

---

## Quick start

### 1) Initialize an instance

```bash
# plain init
depths init

# or initialize with schema add-ons (new in v0.1.3)
depths init --addons http,genai,db
```

This lays out `./depths_data/default` with `configs`, `index`, day `staging`, and a local `stats` area (created on first use).
When you pass `--addons`, your choices are saved to `configs/options.json` and applied automatically at runtime.

### 2) Start the OTLP HTTP server

```bash
# foreground
depths start -F

# or background
depths start
```

By default the service listens on `0.0.0.0:4318` and picks up the `default` instance **without re-running init**, using the options saved earlier (including any add-ons).

Customize:

```bash
depths start -F -I default -H 0.0.0.0 -P 4318
```

The server exposes:

* OTLP ingest: `POST /v1/traces`, `POST /v1/logs`, `POST /v1/metrics`
* Health: `GET /healthz`
* Reads:

  * Raw: `GET /api/spans`, `GET /api/logs`, `GET /api/metrics/points`, `GET /api/metrics/hist`
  * Derived (minute rollups): `GET /api/stats/minute`
  * Real-time: `GET /rt/{signal}` where `{signal}` is `traces | logs | metrics`

### 3) Point your SDK or Collector

Most OTLP HTTP exporters default to port `4318`. Example cURL for JSON:

```bash
curl -X POST http://localhost:4318/v1/logs \
  -H 'content-type: application/json' \
  -d '{"resourceLogs":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"demo"}}]},"scopeLogs":[{"scope":{},"logRecords":[{"timeUnixNano":"1710000000000000000","body":{"stringValue":"hello depths"}}]}]}]}'
```

If you installed the protobuf extra, you can send `application/x-protobuf` too.

---

## The six Delta tables (layout)

Depths writes one Delta table per OTel family under a day root:

```
<instance_root>/staging/days/<YYYY-MM-DD>/otel/
  spans/
  span_events/
  span_links/
  logs/
  metrics_points/
  metrics_hist/
```

### Minute-wise stats (derived store)

A background worker maintains per-minute snapshots and appends to:

```
<instance_root>/stats/otel_minute/
  └── _delta_log, data files partitioned by project_id / event_date
```

Query over HTTP:

```bash
# latest minute snapshots for a service
curl 'http://localhost:4318/api/stats/minute?project_id=demo&service_name=api&limit=200'
```

or read lazily in Python:

```python
from depths.core.logger import DepthsLogger

lg = DepthsLogger()
lf = lg.stats_minute_lazy(project_id="demo", latest_only=True)
print(lf.collect().head(5))
```

### Real-time stream (SSE)

Peek at the newest telemetry as it arrives (before persistence). This is a best-effort tail; some items may never persist.

```bash
# logs stream
curl -N 'http://localhost:4318/rt/logs?n=100&heartbeat_s=10'
```

---

## Schema add-ons (v0.1.3)

Depths can promote selected OpenTelemetry attributes to **first-class columns** across the six tables. Choose any combination when you run `depths init --addons ...`. Unlisted attributes are preserved under the appropriate `*_attrs_json` column.

Built-in add-ons:

| Add-on     | Tables                                    | Columns added (selected)                                                                                             |
| ---------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **device** | all 6                                     | `os_name`, `os_version`, `device_model`                                                                              |
| **geo**    | all 6                                     | `geo_continent_code`, `geo_country_iso_code`, `geo_locality_name`, `geo_attrs_json`                                  |
| **http**   | spans, logs                               | `http_method`, `http_route`, `http_status_code`, `url_path`, `url_query`, `client_address`, `http_attrs_json`        |
| **rpc**    | spans, logs                               | `rpc_system`, `rpc_service`, `rpc_method`, `rpc_grpc_status_code`, `rpc_attrs_json`                                  |
| **db**     | spans, logs                               | `db_system`, `db_name`, `db_operation`, `db_statement_hash`, `db_response_status_code`, `db_attrs_json`              |
| **genai**  | spans, logs, metrics_points, metrics_hist | `genai_provider`, `genai_model`, `genai_input_tokens`, `genai_output_tokens`, `genai_latency_ms`, `genai_attrs_json` |

Enable at init:

```bash
depths init --addons http,genai,db
```

or programmatically:

```python
from depths.core.logger import DepthsLogger
from depths.core.config import DepthsLoggerOptions

opts = DepthsLoggerOptions(addons=["http","genai","db"])
lg = DepthsLogger(options=opts)
```

### Querying add-on columns

Add-on columns are available like any other field:

```bash
curl 'http://localhost:4318/api/logs?project_id=genai_demo&service_name=genai_service&body_like=demo&select=event_ts,service_name,genai_provider,genai_model,genai_input_tokens,genai_output_tokens,genai_latency_ms,genai_attrs_json,body&max_rows=200'
```

Any remaining `gen_ai.*`, `http.*`, `rpc.*`, `db.*`, or `geo.*` attributes not promoted are preserved in their `*_attrs_json` column.

---

## Reading your data (raw tables)

Each endpoint accepts useful filters and returns JSON rows.

```bash
# last 100 logs with severity >= 9 that contain "error"
curl 'http://localhost:4318/api/logs?severity_ge=9&body_like=error&max_rows=100'
```

```bash
# metric points for a gauge/sum instrument
curl 'http://localhost:4318/api/metrics/points?project_id=demo&instrument_name=req_latency_ms&max_rows=100'
```

Programmatic reads:

```python
from depths.core.logger import DepthsLogger

logger = DepthsLogger()
rows = logger.read_logs(body_like="timeout", max_rows=50)
print(rows[:3])
```

---

## Identity context (opt-in)

Depths can enrich rows with **session** and **user** identity, following current OpenTelemetry attribute conventions. It’s **off by default**.

Enable via options (Python) or by editing `configs/options.json`:

```python
from depths.core.logger import DepthsLogger
from depths.core.config import DepthsLoggerOptions

opts = DepthsLoggerOptions(
    add_session_context=True,
    add_user_context=True,
)

lg = DepthsLogger(options=opts)
```

When enabled, Depths reads these keys from event attributes first (then resource attributes):

* `session.id` → `session_id`
* `session.previous_id` → `session_previous_id`
* `user.id` → `user_id`
* `user.name` → `user_name`
* `user.roles` (list of strings) → `user_roles_json` (JSON-encoded)

When disabled, the columns remain empty.

---

## S3 shipping

Turn on shipping and the background worker will seal completed days and upload them to S3, then verify remote rowcounts and clean the local day on a match.

S3 is configured from environment variables. A typical flow is:

1. Run with S3 configured in the environment
2. Depths rolls over at UTC midnight and enqueues yesterday for shipping
3. Shipper seals each Delta table, uploads, verifies, and cleans the local day

---

## Configuration

* Instance identity and data dir come from `DEPTHS_INSTANCE_ID` and `DEPTHS_INSTANCE_DIR` (the CLI sets these).
* S3 configuration is read from environment variables.
* Runtime knobs (queues, flush triggers, shipper timeouts, stats cadence, real-time caps, identity context, and **schema add-ons**) live in the options object (`depths.core.config.DepthsLoggerOptions`). Add-on names are stored as a JSON array under `addons` in `configs/options.json`.

---

## Development notes

* Package import is `depths` and can be installed with the protobuf extra using `depths[proto]`.
* The service lives at `depths.cli.app:app` for uvicorn.
* CLI commands are available as `depths init`, `depths start`, and `depths stop`.

---

## Status

Version `v0.1.3`. Adds **schema add-ons** (HTTP/RPC/DB/Device/Geo/GenAI) and `depths init --addons ...`, while keeping minute rollups, the real-time stream, and optional identity context. The docs are the best place to start: **[https://docs.depthsai.com](https://docs.depthsai.com)**.

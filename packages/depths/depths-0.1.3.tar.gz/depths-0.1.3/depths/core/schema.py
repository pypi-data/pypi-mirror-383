"""
======================================================================
(A) FILE PATH & IMPORT PATH
depths/core/schema.py  →  import path: depths.core.schema
======================================================================

======================================================================
(B) FILE OVERVIEW (concept & significance in v0.1.3)
Canonical, typed schemas with built-in niche specific add-ons for the six OTel tables that Depths v0.1.3
persists as Delta Lake tables. This module provides:
  • EventSchema         → declarative table contract used by Producer/Aggregator
  • SchemaDelta         → dataclass to extend the EventSchema for specified OTel tables with niche specific add-on
  • compose_schema and apply_addons → public helper functions to modify the base EventSchema with chosen add-ons, generating modified EventSchema objects
  • RESOURCE_SCOPE_BASE → normalized columns shared by all six tables
  • SPAN_SCHEMA, SPAN_EVENT_SCHEMA, SPAN_LINK_SCHEMA
  • LOG_SCHEMA, METRIC_POINT_SCHEMA, METRIC_HIST_SCHEMA


Choice of built-in addons: Chosen for maximum surface area with 5-6 add-on templates. More to come in later versions.

These schemas anchor:
  - Validation & normalization in depths.core.producer.LogProducer
  - DataFrame construction & Delta writes in depths.core.aggregator.LogAggregator
  - OTLP JSON → row mapping in depths.core.otlp_mapper.OTLPMapper
  - Reader projections in depths.core.logger.DepthsLogger

Design goals: OTel-first column names, UTC event day alignment, safe
JSON encoding of attribute blobs, and stable partitions (notably
project_id, service_name, schema_version).
======================================================================

======================================================================
(C) IMPORTS & GLOBALS (what & why)
dataclasses, typing  → immutable schema descriptor with rich metadata
polars as pl        → column dtypes used for validation & DF typing
datetime            → helper for timestamp→date coercions

Globals defined:
  - RESOURCE_SCOPE_BASE: shared columns (resource/scope + event_ts/date)
  - <SCHEMA> constants: SPAN_SCHEMA, SPAN_EVENT_SCHEMA, SPAN_LINK_SCHEMA,
    LOG_SCHEMA, METRIC_POINT_SCHEMA, METRIC_HIST_SCHEMA
    (each is an EventSchema instance consumed by Producer/Aggregator/Logger).
======================================================================
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Set, Tuple, Literal, Optional
import polars as pl
import datetime as _dt

@dataclass(frozen=True)
class EventSchema:
    """
    Declarative contract for a concrete Delta table.

    Overview (v0.1.3 role):
        EventSchema is the single source of truth for table shape & behavior
        across the ingestion path. LogProducer uses it to validate/normalize
        rows; LogAggregator uses `polars_schema()` to type DataFrames and create
        Delta tables; OTLPMapper aligns its output to the required/default/
        computed fields. DepthsLogger wires the six OTel tables by attaching
        the corresponding EventSchema to producer/aggregator configs.

    Fields:
        fields:  Polars dtype mapping for all columns (column name → pl.DataType).
        required: Set of required columns after defaults/computed are applied.
        defaults: Column → default value (applied if not present on input).
        computed: Column → callable(row_dict) producing derived values.
        extra_policy: How to treat unexpected keys ('error' | 'strip' | 'keep').
        autocoerce: Allow Producer to cast simple types (e.g., "1" → 1).
        json_fields: Columns that must be JSON-encoded strings on disk.
        enforce_date_from_ts: Optional (ts_ms_field, date_str_field) to
                              enforce UTC day coherence (e.g., event_ts → event_date).
        schema_version: Logical version for downstream partitioning/evolution.

    Returns:
        (N/A — dataclass)

    Notes:
        - All JSON-like columns are modeled as pl.Utf8; Producer serializes to JSON.
        - event_ts is epoch milliseconds; event_date is 'YYYY-MM-DD' (UTC).
        - service_name defaults to 'unknown' to keep partitions non-empty.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Frozen for safety: treat schemas as constants.
    # - Keep column names aligned with OTLP terminology for intuitive queries.
    # - Adding columns: extend `fields` + defaults and (optionally) required.
    # - Renames/removals are backward-incompatible: plan migrations if needed.

    fields: Dict[str, pl.DataType]
    required: Set[str] = field(default_factory=set)
    defaults: Dict[str, Any] = field(default_factory=dict)
    computed: Dict[str, Callable[[Mapping[str, Any]], Any]] = field(default_factory=dict)
    extra_policy: Literal["error", "strip", "keep"] = "strip"
    autocoerce: bool = True
    json_fields: Set[str] = field(default_factory=set)
    enforce_date_from_ts: Tuple[str, str] | None = None  
    schema_version: int = 1

    def polars_schema(self) -> Dict[str, pl.DataType]:
        """
        Return the Polars schema mapping for this table.

        Overview (v0.1.3 role):
            Used by the Aggregator when creating schema-only Delta tables and when
            constructing typed DataFrames for append writes.

        Returns:
            Mapping of column name → pl.DataType.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Intentionally returns the `fields` dict verbatim.
        # - Keep dtypes stable; changes ripple into persisted Delta metadata.

        return self.fields

@dataclass
class SchemaDelta:
    """
    Minimal patch to extend an EventSchema.

    Overview (NEW in v0.1.3):
        Schema add-ons are deterministic "patches" that extend the six OTel
        tables with extra columns/defaults/computed fns/json_fields. We keep
        base schemas intact and compose add-ons at runtime to produce the
        final EventSchema used by Producer/Aggregator.

    Fields:
        fields:      Column name → pl.DataType to add/override.
        required:    Additional required columns (rare; prefer defaults).
        defaults:    Column → default value (applied if absent).
        computed:    Column → callable(row_dict) for derived values.
        json_fields: Columns to be JSON-encoded strings on disk.

    Developer Notes:
        - Intended to be *composed* into base EventSchema; does not remove fields.
        - Prefer adding only stable, frequently used semconv attributes.
        - Keep promoted columns minimal & semconv-aligned.
        - All *_attrs_json are pl.Utf8 and must be listed in json_fields.
        - Defaults use "", 0, 0.0, "{}", or "[]" consistently.
        - No legacy fallbacks handled at schema level (mapper decides inputs).
    """
    fields: Dict[str, pl.DataType] = field(default_factory=dict)
    required: Set[str] = field(default_factory=set)
    defaults: Dict[str, Any] = field(default_factory=dict)
    computed: Dict[str, Callable[[Mapping[str, Any]], Any]] = field(default_factory=dict)
    json_fields: Set[str] = field(default_factory=set)

def _ns_to_ms(ns: int) -> int:
    """
    Convert UNIX epoch nanoseconds → milliseconds (floor division).

    Overview (v0.1.3 role):
        Normalizes OTLP's nanosecond timestamps to the millisecond epoch used
        in event_ts across all tables.

    Args:
        ns: UNIX timestamp in nanoseconds.

    Returns:
        Milliseconds since epoch as int.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Keep arithmetic integer-only to avoid float rounding artifacts.
    # - Used by computed fields in multiple schemas; must remain deterministic.

    return int(ns // 1_000_000)

def _ms_to_date(ms: int) -> str:
    """
    Convert epoch milliseconds → UTC date string ('YYYY-MM-DD').

    Overview (v0.1.3 role):
        Provides the canonical UTC day used for event_date partitions
        and date coherence checks in the Producer.

    Args:
        ms: Milliseconds since epoch.

    Returns:
        UTC date in ISO format YYYY-MM-DD.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - UTC only (no timezone offsets). Aligns with S3/day layout and readers.
    # - Keep format stable; many call sites depend on exact 'YYYY-MM-DD'.

    return _dt.datetime.fromtimestamp(ms / 1000, tz=_dt.timezone.utc).strftime("%Y-%m-%d")

def compose_schema(base: EventSchema, delta: SchemaDelta) -> EventSchema:
    """
    Merge a base EventSchema with a SchemaDelta (pure function).

    Overview:
        Returns a *new* EventSchema with additive changes. We do not
        mutate the base and we never drop columns here.

    Args:
        base:  Existing EventSchema constant (e.g., LOG_SCHEMA).
        delta: Patch describing additional columns/defaults/json_fields.

    Returns:
        A new EventSchema reflecting base + delta.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Preserve base.extra_policy/autocoerce/enforce_date_from_ts/schema_version.
    # - json_fields is a set union; defaults are shallow-merged (delta wins).
    return EventSchema(
        fields={**base.fields, **delta.fields},
        required=set(base.required) | set(delta.required),
        defaults={**base.defaults, **delta.defaults},
        computed={**base.computed, **delta.computed},
        extra_policy=base.extra_policy,
        autocoerce=base.autocoerce,
        json_fields=set(base.json_fields) | set(delta.json_fields),
        enforce_date_from_ts=base.enforce_date_from_ts,
        schema_version=base.schema_version,
    )


# Doc:
# Canonical six table keys used throughout the file when applying add-ons.

# --- DEVELOPER NOTES -----------------------------------------------------
# - Keep names in sync with depths.core.logger construction order.
_ALL_TABLE_KEYS: Tuple[str, ...] = (
    "spans", "span_events", "span_links", "logs", "metrics_points", "metrics_hist"
)


def _device_delta() -> SchemaDelta:
    """
    Device/OS (Resource-level) add-on applied to all six tables.

    Columns:
        os_name, os_version, device_model (Utf8)

    Rationale:
        Resource describes the producing entity; safe to project everywhere.
    """
    return SchemaDelta(
        fields={
            "os_name": pl.Utf8,
            "os_version": pl.Utf8,
            "device_model": pl.Utf8,
        },
        defaults={
            "os_name": "", "os_version": "", "device_model": "",
        },
    )


def _geo_delta() -> SchemaDelta:
    """
    Geo (Resource-level or client.geo.*) add-on applied to all six tables.

    Columns:
        geo_continent_code (Utf8), geo_country_iso_code (Utf8),
        geo_locality_name (Utf8), geo_attrs_json (Utf8; JSON)

    Rationale:
        Geo is often client-derived but may be resource-bound in some setups.
        We project the stable trio to columns; everything else under geo.*
        is preserved in geo_attrs_json.
    """
    return SchemaDelta(
        fields={
            "geo_continent_code": pl.Utf8,
            "geo_country_iso_code": pl.Utf8,
            "geo_locality_name": pl.Utf8,
            "geo_attrs_json": pl.Utf8,
        },
        defaults={
            "geo_continent_code": "",
            "geo_country_iso_code": "",
            "geo_locality_name": "",
            "geo_attrs_json": "{}",
        },
        json_fields={"geo_attrs_json"},
    )


def _http_delta() -> SchemaDelta:
    """
    HTTP add-on (spans/logs).

    Columns:
        http_method (Utf8), http_route (Utf8), http_status_code (Int64),
        url_path (Utf8), url_query (Utf8), client_address (Utf8),
        http_attrs_json (Utf8; JSON)

    Notes:
        - url.path/url.query are the current semconv split of http.target.
    """
    return SchemaDelta(
        fields={
            "http_method": pl.Utf8,
            "http_route": pl.Utf8,
            "http_status_code": pl.Int64,
            "url_path": pl.Utf8,
            "url_query": pl.Utf8,
            "client_address": pl.Utf8,
            "http_attrs_json": pl.Utf8,
        },
        defaults={
            "http_method": "", "http_route": "",
            "http_status_code": 0,
            "url_path": "", "url_query": "",
            "client_address": "",
            "http_attrs_json": "{}",
        },
        json_fields={"http_attrs_json"},
    )


def _rpc_delta() -> SchemaDelta:
    """
    RPC/gRPC add-on (spans/logs).

    Columns:
        rpc_system (Utf8), rpc_service (Utf8), rpc_method (Utf8),
        rpc_grpc_status_code (Int64), rpc_attrs_json (Utf8; JSON)
    """
    return SchemaDelta(
        fields={
            "rpc_system": pl.Utf8,
            "rpc_service": pl.Utf8,
            "rpc_method": pl.Utf8,
            "rpc_grpc_status_code": pl.Int64,
            "rpc_attrs_json": pl.Utf8,
        },
        defaults={
            "rpc_system": "", "rpc_service": "", "rpc_method": "",
            "rpc_grpc_status_code": 0,
            "rpc_attrs_json": "{}",
        },
        json_fields={"rpc_attrs_json"},
    )


def _db_delta() -> SchemaDelta:
    """
    Database add-on (spans/logs).

    Columns:
        db_system (Utf8), db_name (Utf8), db_operation (Utf8),
        db_statement_hash (Utf8), db_response_status_code (Utf8),
        db_attrs_json (Utf8; JSON)

    Notes:
        - Raw query text stays in JSON; we expose only a statement hash column.
    """
    return SchemaDelta(
        fields={
            "db_system": pl.Utf8,
            "db_name": pl.Utf8,
            "db_operation": pl.Utf8,
            "db_statement_hash": pl.Utf8,
            "db_response_status_code": pl.Utf8,
            "db_attrs_json": pl.Utf8,
        },
        defaults={
            "db_system": "", "db_name": "", "db_operation": "",
            "db_statement_hash": "", "db_response_status_code": "",
            "db_attrs_json": "{}",
        },
        json_fields={"db_attrs_json"},
    )


def _genai_delta() -> SchemaDelta:
    """
    Generative AI add-on (spans/logs/metrics).

    Columns:
        genai_provider (Utf8), genai_model (Utf8),
        genai_input_tokens (Int64), genai_output_tokens (Int64),
        genai_latency_ms (Float64), genai_attrs_json (Utf8; JSON)
    """
    return SchemaDelta(
        fields={
            "genai_provider": pl.Utf8,
            "genai_model": pl.Utf8,
            "genai_input_tokens": pl.Int64,
            "genai_output_tokens": pl.Int64,
            "genai_latency_ms": pl.Float64,
            "genai_attrs_json": pl.Utf8,
        },
        defaults={
            "genai_provider": "", "genai_model": "",
            "genai_input_tokens": 0, "genai_output_tokens": 0,
            "genai_latency_ms": 0.0,
            "genai_attrs_json": "{}",
        },
        json_fields={"genai_attrs_json"},
    )


# Doc:
# Built-in add-ons → table-specific deltas.
# 
# --- DEVELOPER NOTES -----------------------------------------------------
# - Only create deltas where the semantics justify promotion to columns.
# - device/geo apply to all six tables; http/rpc/db to spans/logs; genai also to metrics.

BUILTIN_ADDONS: Dict[str, Dict[str, SchemaDelta]] = {
    "device": { t: _device_delta() for t in _ALL_TABLE_KEYS },
    "geo":    { t: _geo_delta()    for t in _ALL_TABLE_KEYS },

    "http": {
        "spans": _http_delta(),
        "logs":  _http_delta(),
    },
    "rpc": {
        "spans": _rpc_delta(),
        "logs":  _rpc_delta(),
    },
    "db": {
        "spans": _db_delta(),
        "logs":  _db_delta(),
    },
    "genai": {
        "spans":          _genai_delta(),
        "logs":           _genai_delta(),
        "metrics_points": _genai_delta(),
        "metrics_hist":   _genai_delta(),
    },
}


def apply_addons(schemas: Dict[str, EventSchema], addon_names: Optional[list[str]]) -> Dict[str, EventSchema]:
    """
    Compose selected add-ons onto the provided base schemas. Logger imports apply_addons(...) to build the
    composed schemas per user-selected add-ons.

    Args:
        schemas:     Mapping of table_key → base EventSchema.
        addon_names: Ordered list of add-on names to apply (e.g., ["http","db"]).

    Returns:
        New dict with composed EventSchema per table.

    Behavior:
        - Applies deltas in the given order; merges are deterministic.
        - Unknown add-on names are ignored (logger will validate earlier).
    """
    out = dict(schemas)
    for name in (addon_names or []):
        deltas = BUILTIN_ADDONS.get(name, {})
        if not deltas:
            continue
        for table_key, delta in deltas.items():
            if table_key in out:
                out[table_key] = compose_schema(out[table_key], delta)
    return out

# Doc:
# Shared columns across all six OTel tables: project/service identity,
# resource/scope JSON blobs, and the canonical event time & UTC day.
# Ensures consistent partitioning and query predicates across tables.

# --- DEVELOPER NOTES -----------------------------------------------------
# - event_ts is epoch ms; event_date is derived UTC 'YYYY-MM-DD'.
# - JSON-bearing columns are pl.Utf8; Producer handles JSON serialization.

RESOURCE_SCOPE_BASE: Dict[str, pl.DataType] = {
    "project_id": pl.Utf8,
    "schema_version": pl.Int64,

    "service_name": pl.Utf8,
    "service_namespace": pl.Utf8,
    "service_instance_id": pl.Utf8,
    "service_version": pl.Utf8,
    "deployment_env": pl.Utf8,
    "resource_attrs_json": pl.Utf8,

    "scope_name": pl.Utf8,
    "scope_version": pl.Utf8,
    "scope_attrs_json": pl.Utf8,
    
    "event_ts": pl.Int64,    
    "event_date": pl.Utf8, 
}

# Doc:
# Spans table: each row is a span with start/end times, status, and attributes.
# event_ts/event_date come from start_time_unix_nano; duration_ms is computed.

# --- DEVELOPER NOTES -----------------------------------------------------
# - Required includes event_ts/event_date for partition alignment.
# - service_name is set to "unknown" when NULL, to suitably handle delta partitioning.
# - Defaults set status_code='UNSET', kind='INTERNAL', empty JSONs to '{}'.
# - Keep trace_id/span_id lowercase hex; Producer can enforce lengths.
# - v0.1.2: Added session and user identity context

SPAN_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "trace_id": pl.Utf8,
        "span_id": pl.Utf8,
        "parent_span_id": pl.Utf8,
        "name": pl.Utf8,
        "kind": pl.Utf8,
        "start_time_unix_nano": pl.Int64,
        "end_time_unix_nano": pl.Int64,
        "duration_ms": pl.Float64,
        "status_code": pl.Utf8,
        "status_message": pl.Utf8,
        "dropped_events_count": pl.Int64,
        "dropped_links_count": pl.Int64,
        "span_attrs_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={
        "project_id","schema_version","trace_id","span_id","name",
        "start_time_unix_nano","end_time_unix_nano","event_ts","event_date",
    },
    defaults={
        "schema_version": 1,
        "dropped_events_count": 0, "dropped_links_count": 0,
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",
        "status_code":"UNSET", "status_message":"", "kind":"INTERNAL",
        "parent_span_id":"", "span_attrs_json":"{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("start_time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("start_time_unix_nano", 0)))),
        "duration_ms": lambda d: max(
            0.0, (int(d.get("end_time_unix_nano", 0)) - int(d.get("start_time_unix_nano", 0))) / 1_000_000.0
        ),
    },
    json_fields={"resource_attrs_json","scope_attrs_json","span_attrs_json"},
    enforce_date_from_ts=("event_ts", "event_date"),
    schema_version=1,
)

# Doc:
# Span events table: one row per Span.Event. Timestamps taken from time_unix_nano.

# --- DEVELOPER NOTES -----------------------------------------------------
# - Keep event_attrs_json compact (Producer serializes with separators=(',',':')).
# - Maintain alignment with OTLP LogRecord shape for body/attrs symmetry.
# - v0.1.2: Added session and user identity context

SPAN_EVENT_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "trace_id": pl.Utf8,
        "span_id": pl.Utf8,
        "time_unix_nano": pl.Int64,
        "name": pl.Utf8,
        "event_attrs_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","trace_id","span_id","time_unix_nano","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "name":"", "event_attrs_json":"{}",
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("time_unix_nano", 0)))),
    },
    json_fields={"resource_attrs_json","scope_attrs_json","event_attrs_json"},
    enforce_date_from_ts=("event_ts", "event_date"),
    schema_version=1,
)


# Doc:
# Links between spans. event_ts/event_date are supplied by the Mapper based on
# the *parent span's* start time for stable timeline placement.

# --- DEVELOPER NOTES -----------------------------------------------------
# - No computed fields here by design; Mapper sets event_ts/event_date.
# - linked_trace_id/linked_span_id are lowercase hex strings.
# - v0.1.2: Added session and user identity context

SPAN_LINK_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "trace_id": pl.Utf8,
        "span_id": pl.Utf8,
        "linked_trace_id": pl.Utf8,
        "linked_span_id": pl.Utf8,
        "link_attrs_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","trace_id","span_id","linked_trace_id","linked_span_id","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "link_attrs_json":"{}",
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={},  # as in v0.1.3 (no implicit time derivation here)
    json_fields={"resource_attrs_json","scope_attrs_json","link_attrs_json"},
    enforce_date_from_ts=("event_ts", "event_date"),
    schema_version=1,
)

# Doc:
# OTel logs table. event_ts/event_date derive from time_unix_nano.
# trace_id/span_id may be empty (uncorrelated records are allowed).

# --- DEVELOPER NOTES -----------------------------------------------------
# - body is a string: AnyValue is stringified deterministically by Mapper.
# - severity_number is Int32 for compactness; adjust only with migration.
# - v0.1.2: Added session and user identity context

LOG_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "time_unix_nano": pl.Int64,
        "observed_time_unix_nano": pl.Int64,
        "severity_text": pl.Utf8,
        "severity_number": pl.Int32,
        "body": pl.Utf8,
        "log_attrs_json": pl.Utf8,
        "trace_id": pl.Utf8,
        "span_id": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "observed_time_unix_nano": 0, "severity_text":"", "severity_number":0,
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",
        "log_attrs_json":"{}", "trace_id":"", "span_id":"",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("time_unix_nano", 0)))),
    },
    json_fields={"resource_attrs_json","scope_attrs_json","log_attrs_json"},
    enforce_date_from_ts=("event_ts", "event_date"),
    schema_version=1,
)

# Doc:
# Gauge/Sum points. Carries temporality/monotonicity and a single numeric value.
# event_ts/event_date derive from time_unix_nano.

# --- DEVELOPER NOTES -----------------------------------------------------
# - value coerces to Float64 for uniformity across numeric types.
# - Exemplars/attrs stored as JSON strings for flexibility.
# - Aggregation temporality can be CUMULATIVE|DELTA|UNSPECIFIED
# - v0.1.2: Added session and user identity context

METRIC_POINT_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "instrument_name": pl.Utf8,
        "instrument_type": pl.Utf8,
        "unit": pl.Utf8,                            
        "aggregation_temporality": pl.Utf8,
        "is_monotonic": pl.Boolean,
        "time_unix_nano": pl.Int64,
        "start_time_unix_nano": pl.Int64,
        "value": pl.Float64,
        "point_attrs_json": pl.Utf8,
        "exemplars_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","instrument_name","instrument_type","time_unix_nano","value","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "unit":"", "aggregation_temporality":"UNSPECIFIED", "is_monotonic": False,
        "start_time_unix_nano": 0, "point_attrs_json":"{}", "exemplars_json":"[]",
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json": "{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("time_unix_nano", 0)))),
    },
    json_fields={"resource_attrs_json","scope_attrs_json","point_attrs_json","exemplars_json"},
    enforce_date_from_ts=("event_ts","event_date"),
    schema_version=1,
)


# Doc:
# Instrument type: Histogram / ExpHistogram / Summary family in a single wide table.
# Buckets/bounds/quantiles captured as JSON text fields.

# --- DEVELOPER NOTES -----------------------------------------------------
# - Use Float64 for sum/min/max; counts are Int64; exp_* metadata as ints.
# - event_ts/event_date derive from time_unix_nano; keep UTC semantics stable.
# - v0.1.2: Added session and user identity context

METRIC_HIST_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "instrument_name": pl.Utf8,
        "instrument_type": pl.Utf8,
        "unit": pl.Utf8,
        "aggregation_temporality": pl.Utf8,
        "time_unix_nano": pl.Int64,
        "start_time_unix_nano": pl.Int64,
        "count": pl.Int64,
        "sum": pl.Float64,
        "min": pl.Float64,
        "max": pl.Float64,
        "bounds_json": pl.Utf8,
        "counts_json": pl.Utf8,
        "exp_zero_count": pl.Int64,
        "exp_scale": pl.Int32,
        "exp_positive_json": pl.Utf8,
        "exp_negative_json": pl.Utf8,
        "quantiles_json": pl.Utf8,
        "point_attrs_json": pl.Utf8,
        "exemplars_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","instrument_name","instrument_type","time_unix_nano","count","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "unit":"", "aggregation_temporality":"UNSPECIFIED",
        "start_time_unix_nano": 0, "sum": 0.0, "min": 0.0, "max": 0.0,
        "bounds_json":"[]", "counts_json":"[]",
        "exp_zero_count":0, "exp_scale":0,
        "exp_positive_json":"{}", "exp_negative_json":"{}",
        "quantiles_json":"[]", "point_attrs_json":"{}", "exemplars_json":"[]",
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("time_unix_nano", 0)))),
    },
    json_fields={
        "resource_attrs_json","scope_attrs_json","bounds_json","counts_json",
        "exp_positive_json","exp_negative_json","quantiles_json","point_attrs_json","exemplars_json"
    },
    enforce_date_from_ts=("event_ts","event_date"),
    schema_version=1,
)


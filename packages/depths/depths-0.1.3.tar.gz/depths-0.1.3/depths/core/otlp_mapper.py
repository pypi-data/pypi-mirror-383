"""
======================================================================
(A) FILE PATH & IMPORT PATH
depths/core/otlp_mapper.py  →  import path: depths.core.otlp_mapper
======================================================================

======================================================================
(B) FILE OVERVIEW (concept & significance in v0.1.3)
Stateless translators from decoded OTLP JSON (traces/logs/metrics) to
Depths row dicts aligned with our six OTel Delta tables:
  • Spans, Span Events, Span Links
  • Logs
  • Metric Points (Gauge/Sum) + Metric Hists (Histogram/ExpHistogram/Summary)

Responsibilities:
  - Stamp common Resource & Scope context on every row
  - Normalize correlation IDs to lowercase hex
  - Choose canonical timestamps (ns→ms; UTC date) for downstream schemas
  - Keep attribute-like fields as Python dict/list; Producer JSON-serializes
  - (v0.1.2) Optionally attach Identity Context (user/session) from OTel attrs
  - (v0.1.3) Optionally handle built-on schema expansion add-ons for specific popular niches

Consumers:
  - depths.core.producer.LogProducer (validation/normalization)
  - depths.core.aggregator.LogAggregator (DF construction & Delta writes)
  - depths.core.schema (column shape & date/ts enforcement)

Notable rule: Span Links rows get event_ts/event_date from the *parent
span’s start time* to make links appear at span-begin on timelines.
======================================================================

======================================================================
(C) IMPORTS & GLOBALS (what & why)
typing, json, datetime  → robust parsing & deterministic stringification
hashlib → hashing bulky and PII sensitive strings
Helper fns (_ns_to_ms, _ms_to_date, _any_value_to_py, _attributes_to_dict)
  convert OTLP AnyValue/attributes and handle time conversions.
No module-level mutable globals.
======================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional, Mapping
import json
import datetime as _dt
import hashlib

def _ns_to_ms(ns: int) -> int:
    """
    Convert nanoseconds since UNIX epoch to milliseconds (floor division).

    Overview (v0.1.3 role):
        OTLP timestamps are typically in nanoseconds; our event_ts uses
        milliseconds. This canonical conversion is reused across traces/logs/metrics.

    Args:
        ns: Nanoseconds since UNIX epoch.

    Returns:
        Milliseconds since UNIX epoch as an int.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Keep integer arithmetic to avoid float rounding.
    # - Used to derive event_ts and, via _ms_to_date, event_date.

    return int(ns // 1_000_000)

def _ms_to_date(ms: int) -> str:
    """
    Convert epoch milliseconds to a UTC date string ('YYYY-MM-DD').

    Overview (v0.1.3 role):
        Produces canonical event_date partitions for tables that need explicit
        dates (e.g., span links) or for diagnostics.

    Args:
        ms: Milliseconds since epoch.

    Returns:
        UTC date in ISO format 'YYYY-MM-DD'.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Always UTC; no timezone offsets. Keep format stable.

    return _dt.datetime.fromtimestamp(ms / 1000, tz=_dt.timezone.utc).strftime("%Y-%m-%d")

def _any_value_to_py(v: Dict[str, Any]) -> Any:
    """
    Convert an OTLP AnyValue (JSON shape) into a natural Python value.

    Overview (v0.1.3 role):
        Used by attribute/body parsers so the Producer can later serialize to a
        deterministic JSON string for *_json columns.

    Args:
        v: AnyValue JSON node (stringValue/intValue/doubleValue/boolValue/
           bytesValue/arrayValue/kvlistValue).

    Returns:
        A Python scalar, list, dict, or None matching the AnyValue content.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Arrays and kvlists are converted recursively.
    # - Unknown shapes are returned as-is to avoid lossy handling.

    if v is None:
        return None
    if "stringValue" in v: return v["stringValue"]
    if "boolValue" in v: return bool(v["boolValue"])
    if "intValue" in v: return int(v["intValue"])
    if "doubleValue" in v: return float(v["doubleValue"])
    if "bytesValue" in v: return v["bytesValue"]  
    if "arrayValue" in v:
        arr = v["arrayValue"].get("values", []) or []
        return [_any_value_to_py(x) for x in arr]
    if "kvlistValue" in v:
        kvs = v["kvlistValue"].get("values", []) or []
        out = {}
        for it in kvs:
            out[it.get("key","")] = _any_value_to_py(it.get("value"))
        return out
    return v

def _attributes_to_dict(attrs: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Convert an OTLP KeyValue list (attributes) to a plain Python dict.

    Overview (v0.1.3 role):
        Normalizes resource/scope/span/log/metric attributes; values go through
        `_any_value_to_py` to preserve structure prior to Producer serialization.

    Args:
        attrs: List of {"key": str, "value": AnyValue}-style dicts or None.

    Returns:
        Dict mapping attribute keys to Python values.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Empty/missing input returns {} to keep downstream JSON stable.
    # - Invalid or empty keys are skipped defensively.

    out: Dict[str, Any] = {}
    if not attrs:
        return out
    for kv in attrs:
        k = kv.get("key", "")
        if not k:
            continue
        v = _any_value_to_py(kv.get("value"))
        out[k] = v
    return out

def _stringify_body(body: Dict[str, Any]) -> str:
    """
    Convert LogRecord.body (AnyValue) to a deterministic string.

    Overview (v0.1.3 role):
        Logs.body is stored as a string. We unwrap AnyValue to Python first;
        strings are passed through; other structures are JSON-encoded compactly.

    Args:
        body: AnyValue-like dict from an OTLP LogRecord.

    Returns:
        String representation suitable for the LOGS table `body` column.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - JSON encoding uses compact separators for consistency.
    # - If JSON encoding fails, we fall back to str(py).

    py = _any_value_to_py(body) if body is not None else ""
    if isinstance(py, str):
        return py
    try:
        return json.dumps(py, separators=(",", ":"))
    except Exception:
        return str(py)


def _pick_first(attrs: Mapping[str, Any], rattrs: Mapping[str, Any], *keys: str) -> Optional[Any]:
    """
    Return the first non-empty value among keys from attrs, then resource attrs.
    """
    # Developer notes:
    # - Do not raise on missing keys; leave defaults to schema.
    # - Keep *_attrs_json as *dicts* here; Producer serializes to Utf8.
    for k in keys:
        if k in attrs and attrs[k] not in (None, ""):
            return attrs[k]
    for k in keys:
        if k in rattrs and rattrs[k] not in (None, ""):
            return rattrs[k]
    return None

def _filter_namespace(attrs: Mapping[str, Any], *prefixes: str) -> Dict[str, Any]:
    """
    Shallow-filter attributes by namespace prefixes (e.g., "http.", "url.").
    """
    out: Dict[str, Any] = {}
    for k, v in (attrs or {}).items():
        if any(k.startswith(p) for p in prefixes):
            out[k] = v
    return out

def _sha256_hex(s: str) -> str:
    """
    Compute SHA-256 hex digest of a string; empty string yields "".
    """
    if not s:
        return ""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _lower_hex_or_empty(s: Optional[str]) -> str:
    """
    Normalize a hex identifier (trace/span) to lowercase; empty if missing.

    Args:
        s: TraceId/SpanId candidate string or None.

    Returns:
        Lowercased hex string or "" if falsy.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Length enforcement is performed by Producer when normalization is enabled.

    return (s or "").strip().lower()

class OTLPMapper:
    """
    Stateless mapper: decoded OTLP JSON/dicts → rows for the six OTel tables.

    Overview (v0.1.3 role):
        Centralizes all OTLP-to-row shaping so Producer/Aggregator stay generic.
        Attaches Resource & Scope context, normalizes IDs, chooses timestamp
        sources, and prepares attribute blobs for later JSON serialization.
        (v0.1.2) Optionally enrich rows with Identity Context (user/session).
        (v0.1.3) Respect *schema add-ons* selected at startup:
            • http (spans/logs)     → http_method, http_route, http_status_code, url_path, url_query, client_address, http_attrs_json
            • rpc  (spans/logs)     → rpc_system, rpc_service, rpc_method, rpc_grpc_status_code, rpc_attrs_json
            • db   (spans/logs)     → db_system, db_name, db_operation, db_statement_hash, db_response_status_code, db_attrs_json
            • device (all 6 tables) → os_name, os_version, device_model
            • geo (all 6 tables)    → geo_continent_code, geo_country_iso_code, geo_locality_name, geo_attrs_json
            • genai (spans/logs/metrics) → genai_provider, genai_model, genai_input_tokens, genai_output_tokens, genai_latency_ms, genai_attrs_json

    Methods:
        map_traces(payload, *, project_id)  → (spans, events, links)
        map_logs(payload, *, project_id)    → logs
        map_metrics(payload, *, project_id) → (points, hists)
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Mapper returns *Python* dicts/lists; JSON conversion happens in Producer.
    # - Span Links get event_ts/date from the parent span start (timeline rule).

    def __init__(
        self,
        *,
        default_project_id: str = "default",
        default_service_name: str = "unknown",
        add_session_context: bool = False,
        add_user_context: bool = False,
        enabled_addons: Optional[set[str]] = None,
    ) -> None:
        """
        Initialize the mapper with fallback identity and schema add-ons.

        Args:
            default_project_id: Used when a project_id isn’t supplied at call-time.
            default_service_name: Used if resource attributes lack 'service.name'.
            add_session_context: If True, map session.id/previous_id into rows.
            add_user_context:    If True, map user.id/name/roles into rows.
            enabled_addons:      (NEW v0.1.3) Names of add-ons that should promote
                                 OTel attributes into first-class columns for the
                                 current process (e.g., {"http","db","geo"}).

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Keep defaults aligned with schema defaults and Producer normalization.
        # - `enabled_addons` governs column promotion; everything else remains as JSON.

        self.default_project_id = default_project_id
        self.default_service_name = default_service_name
        self.add_session_context = bool(add_session_context)
        self.add_user_context = bool(add_user_context)
        self.enabled_addons = set(enabled_addons or set())
        
    def _extract_identity(
        self,
        event_attrs: Optional[Dict[str, Any]],
        resource_attrs: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build the optional identity dict from event attrs (preferred) falling back
        to resource attrs. Only returns keys when corresponding toggles are ON.

        Expected OTel keys (current semantics):
          - session.id → session_id
          - session.previous_id → session_previous_id
          - user.id → user_id
          - user.name → user_name
          - user.roles (list[str]|str) → user_roles_json (JSON array string)
        """
        if not (self.add_session_context or self.add_user_context):
            return {}

        ea = event_attrs or {}
        ra = resource_attrs or {}
        out: Dict[str, Any] = {}

        if self.add_session_context:
            sid = ea.get("session.id", ra.get("session.id", "")) or ""
            spid = ea.get("session.previous_id", ra.get("session.previous_id", "")) or ""
            out["session_id"] = str(sid)
            out["session_previous_id"] = str(spid)

        if self.add_user_context:
            uid = ea.get("user.id", ra.get("user.id", "")) or ""
            uname = ea.get("user.name", ra.get("user.name", "")) or ""
            roles = ea.get("user.roles", ra.get("user.roles"))
            if isinstance(roles, list):
                roles_arr = [str(x) for x in roles]
            elif roles is None:
                roles_arr = []
            else:
                roles_arr = [str(roles)]
            out["user_id"] = str(uid)
            out["user_name"] = str(uname)
            out["user_roles_json"] = json.dumps(roles_arr, separators=(",", ":"))

        return out

    def _apply_http(self, row: Dict[str, Any], attrs: Dict[str, Any], rattrs: Dict[str, Any]) -> None:
        """
        Project HTTP attributes into first-class columns for spans/logs.

        Columns:
            http_method, http_route, http_status_code, url_path, url_query,
            client_address, http_attrs_json
        """
        method = _pick_first(attrs, rattrs, "http.request.method")
        route  = _pick_first(attrs, rattrs, "http.route")
        status = _pick_first(attrs, rattrs, "http.response.status_code")
        path   = _pick_first(attrs, rattrs, "url.path")
        query  = _pick_first(attrs, rattrs, "url.query")
        addr   = _pick_first(attrs, rattrs, "client.address")

        if method is not None: row["http_method"] = str(method)
        if route  is not None: row["http_route"] = str(route)
        if status is not None: row["http_status_code"] = int(status)
        if path   is not None: row["url_path"] = str(path)
        if query  is not None: row["url_query"] = str(query)
        if addr   is not None: row["client_address"] = str(addr)

        block = {}
        block.update(_filter_namespace(attrs, "http.", "url."))
        if block:
            row["http_attrs_json"] = block

    def _apply_rpc(self, row: Dict[str, Any], attrs: Dict[str, Any], rattrs: Dict[str, Any]) -> None:
        """
        Project RPC/gRPC attributes into first-class columns for spans/logs.

        Columns:
            rpc_system, rpc_service, rpc_method, rpc_grpc_status_code, rpc_attrs_json
        """
        system = _pick_first(attrs, rattrs, "rpc.system")
        service= _pick_first(attrs, rattrs, "rpc.service")
        method = _pick_first(attrs, rattrs, "rpc.method")
        code   = _pick_first(attrs, rattrs, "rpc.grpc.status_code")

        if system is not None: row["rpc_system"] = str(system)
        if service is not None: row["rpc_service"] = str(service)
        if method is not None: row["rpc_method"] = str(method)
        if code   is not None: row["rpc_grpc_status_code"] = int(code)

        block = _filter_namespace(attrs, "rpc.")
        if block:
            row["rpc_attrs_json"] = block

    def _apply_db(self, row: Dict[str, Any], attrs: Dict[str, Any], rattrs: Dict[str, Any]) -> None:
        """
        Project DB attributes into first-class columns for spans/logs.

        Columns:
            db_system, db_name, db_operation, db_statement_hash,
            db_response_status_code, db_attrs_json
        """
        system = _pick_first(attrs, rattrs, "db.system")
        # Prefer db.namespace; fall back to db.name if present
        dbname = _pick_first(attrs, rattrs, "db.namespace") or _pick_first(attrs, rattrs, "db.name")
        oper   = _pick_first(attrs, rattrs, "db.operation.name")
        resp   = _pick_first(attrs, rattrs, "db.response.status_code")
        qtext  = _pick_first(attrs, rattrs, "db.query.text")

        if system is not None: row["db_system"] = str(system)
        if dbname is not None: row["db_name"] = str(dbname)
        if oper   is not None: row["db_operation"] = str(oper)
        if resp   is not None: row["db_response_status_code"] = str(resp)
        if isinstance(qtext, str) and qtext:
            row["db_statement_hash"] = _sha256_hex(qtext)

        block = _filter_namespace(attrs, "db.")
        if block:
            row["db_attrs_json"] = block

    def _apply_device(self, row: Dict[str, Any], rattrs: Dict[str, Any]) -> None:
        """
        Project Resource device/OS attributes (applies to all six tables).

        Columns:
            os_name, os_version, device_model
        """
        osn = rattrs.get("os.name")
        osv = rattrs.get("os.version")
        dmn = rattrs.get("device.model.name")
        if osn is not None: row["os_name"] = str(osn)
        if osv is not None: row["os_version"] = str(osv)
        if dmn is not None: row["device_model"] = str(dmn)

    def _apply_geo(self, row: Dict[str, Any], attrs: Dict[str, Any], rattrs: Dict[str, Any]) -> None:
        """
        Project Geo attributes (applies to all six tables).

        Columns:
            geo_continent_code, geo_country_iso_code, geo_locality_name, geo_attrs_json

        Notes:
            - Prefer resource-level 'geo.*' when present; else use event attrs.
            - We also capture *all* geo.* keys from event attrs into geo_attrs_json.
        """
        def pick_geo(key: str) -> Optional[Any]:
            if key in rattrs and rattrs[key] not in (None, ""):
                return rattrs[key]
            if key in attrs and attrs[key] not in (None, ""):
                return attrs[key]
            return None

        cont = pick_geo("geo.continent.code")
        ctry = pick_geo("geo.country.iso_code")
        loca = pick_geo("geo.locality.name")

        if cont is not None: row["geo_continent_code"] = str(cont)
        if ctry is not None: row["geo_country_iso_code"] = str(ctry)
        if loca is not None: row["geo_locality_name"] = str(loca)

        block = _filter_namespace(attrs, "geo.")
        if block:
            row["geo_attrs_json"] = block

    def _apply_genai(self, row: Dict[str, Any], attrs: Dict[str, Any], rattrs: Dict[str, Any]) -> None:
        """
        Project Generative AI attributes (spans/logs/metrics).

        Columns:
            genai_provider, genai_model, genai_input_tokens,
            genai_output_tokens, genai_latency_ms, genai_attrs_json
        """
        provider = _pick_first(attrs, rattrs, "gen_ai.provider.name")
        model = _pick_first(attrs, rattrs, "gen_ai.response.model") or _pick_first(attrs, rattrs, "gen_ai.request.model")
        itok = _pick_first(attrs, rattrs, "gen_ai.usage.input_tokens")
        otok = _pick_first(attrs, rattrs, "gen_ai.usage.output_tokens")
        lat  = _pick_first(attrs, rattrs, "gen_ai.latency.ms")

        if provider is not None: row["genai_provider"] = str(provider)
        if model    is not None: row["genai_model"] = str(model)
        if itok     is not None: row["genai_input_tokens"] = int(itok)
        if otok     is not None: row["genai_output_tokens"] = int(otok)
        if lat      is not None: row["genai_latency_ms"] = float(lat)

        block = _filter_namespace(attrs, "gen_ai.")
        if block:
            row["genai_attrs_json"] = block

    def _apply_addons_to_row(self, table_key: str, row: Dict[str, Any], attrs: Dict[str, Any], rattrs: Dict[str, Any]) -> None:
        """
        Dispatch add-on appliers for a given table_key.

        Args:
            table_key: One of {"spans","span_events","span_links","logs","metrics_points","metrics_hist"}.
            row:       Row dict to mutate.
            attrs:     Event-level attributes (span/log/point).
            rattrs:    Resource attributes (for device/geo and fallbacks).
        """
        # device/geo → all tables
        if "device" in self.enabled_addons:
            self._apply_device(row, rattrs)
        if "geo" in self.enabled_addons:
            self._apply_geo(row, attrs, rattrs)

        # http/rpc/db → spans/logs only
        if table_key in ("spans", "logs"):
            if "http" in self.enabled_addons:
                self._apply_http(row, attrs, rattrs)
            if "rpc" in self.enabled_addons:
                self._apply_rpc(row, attrs, rattrs)
            if "db" in self.enabled_addons:
                self._apply_db(row, attrs, rattrs)

        # genai → spans/logs/metrics
        if table_key in ("spans", "logs", "metrics_points", "metrics_hist"):
            if "genai" in self.enabled_addons:
                self._apply_genai(row, attrs, rattrs)


    def _resource_scope_base(self, project_id: Optional[str], resource: Dict[str, Any], scope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the common per-row prefix from Resource & Scope.

        Overview (v0.1.3 role):
            Produces a dict with stable identity and attribute JSON blobs that will
            be merged into every row for the current resource/scope.

        Args:
            project_id: Explicit project id, or None to use default.
            resource:   OTLP Resource dict (with 'attributes').
            scope:      OTLP Scope/InstrumentationLibrary dict (with 'attributes').

        Returns:
            Dict with keys (current implementation):
            • project_id, schema_version
            • service_name, service_namespace, service_instance_id, service_version
            • deployment_env
            • resource_attrs_json (dict)
            • scope_name, scope_version, scope_attrs_json (dict)
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - service_name fallback is default_service_name if not present in Resource.
        # - Values for *_attrs_json remain dicts; Producer serializes to strings.

        rattrs = _attributes_to_dict((resource or {}).get("attributes"))
        scope_attrs = _attributes_to_dict((scope or {}).get("attributes"))
        service_name = rattrs.get("service.name") or self.default_service_name
        base = {
            "project_id": project_id or self.default_project_id,
            "schema_version": 1,
            "service_name": service_name,
            "service_namespace": rattrs.get("service.namespace", ""),
            "service_instance_id": rattrs.get("service.instance.id", ""),
            "service_version": rattrs.get("service.version", ""),
            "deployment_env": rattrs.get("deployment.environment", ""),
            "resource_attrs_json": rattrs,          
            "scope_name": scope.get("name", "") if scope else "",
            "scope_version": scope.get("version", "") if scope else "",
            "scope_attrs_json": scope_attrs,       
        }
        return base

    def map_traces(self, payload: Dict[str, Any], *, project_id: Optional[str] = None) -> Tuple[List[dict], List[dict], List[dict]]:
        """
        Map OTLP Traces JSON to rows for SPANS, SPAN_EVENTS, and SPAN_LINKS tables.

        Overview (v0.1.3 role):
            Iterates resourceSpans → scopeSpans → spans. Emits:
            - Spans: basic span fields + span_attrs_json (event_ts/date computed by schema from start_time_unix_nano)
            - Events: one row per Span.Event (event_ts/date computed by schema from time_unix_nano)
            - Links:  one row per Span.Link with event_ts/date set to the PARENT
                        span’s start (for stable timeline placement)

        Args:
            payload: Decoded OTLP trace export JSON/dict.
            project_id: Optional override for project tenancy.

        Returns:
            (spans_out, events_out, links_out) lists of row dicts.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - ID fields normalized via _lower_hex_or_empty.
        # - span_start_ms is cached to stamp link event_ts/date quickly.
        # - Keep field names aligned with SPAN/… schemas (schema.py).
        # - event_ts/event_date computed by schema from start_time_unix_nano/time_unix_nano
        # - v0.1.2: Added option session + user identity context
        # - v0.1.3: Added schema add-on parsing handling

        spans_out: List[dict] = []
        events_out: List[dict] = []
        links_out: List[dict] = []

        span_start_ms: Dict[Tuple[str, str], int] = {}

        for rs in payload.get("resourceSpans", []) or []:
            resource = rs.get("resource") or {}
            scopes = rs.get("scopeSpans") or rs.get("instrumentationLibrarySpans") or []
            for ss in scopes:
                scope = ss.get("scope") or ss.get("instrumentationLibrary") or {}
                base = self._resource_scope_base(project_id, resource, scope)
                rattrs = base.get("resource_attrs_json", {})  # dict

                for sp in ss.get("spans", []) or []:
                    trace_id = _lower_hex_or_empty(sp.get("traceId"))
                    span_id = _lower_hex_or_empty(sp.get("spanId"))
                    parent_span_id = _lower_hex_or_empty(sp.get("parentSpanId"))
                    start_ns = int(sp.get("startTimeUnixNano", 0) or 0)
                    end_ns = int(sp.get("endTimeUnixNano", 0) or 0)
                    start_ms = _ns_to_ms(start_ns)
                    span_attrs = _attributes_to_dict(sp.get("attributes"))

                    span_row = {
                        **base,
                        "trace_id": trace_id,
                        "span_id": span_id,
                        "parent_span_id": parent_span_id,
                        "name": sp.get("name", "") or "",
                        "kind": sp.get("kind", "") or "",
                        "start_time_unix_nano": start_ns,
                        "end_time_unix_nano": end_ns,
                        "status_code": (sp.get("status") or {}).get("code", "") or "",
                        "status_message": (sp.get("status") or {}).get("message", "") or "",
                        "dropped_events_count": int(sp.get("droppedEventsCount", 0) or 0),
                        "dropped_links_count": int(sp.get("droppedLinksCount", 0) or 0),
                        "span_attrs_json": span_attrs,
                    }
                    # Identity (optional)
                    ident = self._extract_identity(span_attrs, rattrs)
                    if ident:
                        span_row.update(ident)

                    # NEW in v0.1.3 — apply enabled schema add-ons (span)
                    self._apply_addons_to_row("spans", span_row, span_attrs, rattrs)

                    spans_out.append(span_row)
                    span_start_ms[(trace_id, span_id)] = start_ms

                    for ev in sp.get("events", []) or []:
                        ev_ts = int(ev.get("timeUnixNano", 0) or 0)
                        ev_attrs = _attributes_to_dict(ev.get("attributes"))
                        ev_row = {
                            **base,
                            "trace_id": trace_id,
                            "span_id": span_id,
                            "time_unix_nano": ev_ts,
                            "name": ev.get("name", "") or "",
                            "event_attrs_json": ev_attrs,
                        }
                        ident = self._extract_identity(ev_attrs, rattrs)
                        if ident:
                            ev_row.update(ident)

                        self._apply_addons_to_row("span_events", ev_row, ev_attrs, rattrs)

                        events_out.append(ev_row)

                    for lk in sp.get("links", []) or []:
                        linked_tid = _lower_hex_or_empty(lk.get("traceId"))
                        linked_sid = _lower_hex_or_empty(lk.get("spanId"))
                        lk_attrs = _attributes_to_dict(lk.get("attributes"))
                        start_ms = span_start_ms.get((trace_id, span_id), 0)
                        lk_row = {
                            **base,
                            "trace_id": trace_id,
                            "span_id": span_id,
                            "linked_trace_id": linked_tid,
                            "linked_span_id": linked_sid,
                            "link_attrs_json": lk_attrs,
                            "event_ts": start_ms,
                            "event_date": _ms_to_date(start_ms) if start_ms else "1970-01-01",
                        }
                        ident = self._extract_identity(lk_attrs, rattrs)
                        if ident:
                            lk_row.update(ident)

                        self._apply_addons_to_row("span_links", lk_row, lk_attrs, rattrs)

                        links_out.append(lk_row)

        return spans_out, events_out, links_out

    def map_logs(self, payload: Dict[str, Any], *, project_id: Optional[str] = None) -> List[dict]:
        """
        Map OTLP Logs JSON to LOGS table rows.

        Overview (v0.1.3 role):
            Iterates resourceLogs → scopeLogs → logRecords. Converts body AnyValue
            to a string consistently, stamps correlation IDs when present, and
            preserves attributes in log_attrs_json.

        Args:
            payload: Decoded OTLP log export JSON/dict.
            project_id: Optional override for project tenancy.

        Returns:
            logs_out: List of row dicts.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - event_ts/date are computed downstream from time_unix_nano by schema.
        # - trace/span IDs may be empty (uncorrelated records are allowed).
        # - v0.1.2: Added option session + user identity context
        # - v0.1.3: Added schema add-on parsing handling

        logs_out: List[dict] = []

        for rl in payload.get("resourceLogs", []) or []:
            resource = rl.get("resource") or {}
            scopes = rl.get("scopeLogs") or rl.get("instrumentationLibraryLogs") or []
            for sl in scopes:
                scope = sl.get("scope") or sl.get("instrumentationLibrary") or {}
                base = self._resource_scope_base(project_id, resource, scope)
                rattrs = base.get("resource_attrs_json", {})  # dict

                for rec in sl.get("logRecords", []) or []:
                    time_ns = int(rec.get("timeUnixNano", 0) or 0)
                    obs_ns = int(rec.get("observedTimeUnixNano", 0) or 0)
                    body = rec.get("body") or {}
                    log_attrs = _attributes_to_dict(rec.get("attributes"))

                    trace_id = _lower_hex_or_empty(rec.get("traceId"))
                    span_id = _lower_hex_or_empty(rec.get("spanId"))

                    row = {
                        **base,
                        "time_unix_nano": time_ns,
                        "observed_time_unix_nano": obs_ns,
                        "severity_text": rec.get("severityText", "") or "",
                        "severity_number": int(rec.get("severityNumber", 0) or 0),
                        "body": _stringify_body(body),
                        "log_attrs_json": log_attrs,
                        "trace_id": trace_id,
                        "span_id": span_id,
                    }
                    ident = self._extract_identity(log_attrs, rattrs)
                    if ident:
                        row.update(ident)

                    # NEW in v0.1.3 — apply enabled schema add-ons (log)
                    self._apply_addons_to_row("logs", row, log_attrs, rattrs)
                    logs_out.append(row)

        return logs_out

    def map_metrics(self, payload: Dict[str, Any], *, project_id: Optional[str] = None) -> Tuple[List[dict], List[dict]]:
        """
        Map OTLP Metrics JSON to METRIC_POINT and METRIC_HIST rows.

        Overview (v0.1.3 role):
            Iterates resourceMetrics → scopeMetrics → metrics. Emits:
            - Points (Gauge/Sum): instrument_name/type, unit, temporality, is_monotonic,
                time_unix_nano/start_time_unix_nano, value, point_attrs_json, exemplars_json.
            - Hists (Histogram/ExpHistogram/Summary): unified wide shape with counts/sum,
                explicit bounds & counts (or exp buckets), quantiles, attrs, exemplars.

        Args:
            payload: Decoded OTLP metrics export JSON/dict.
            project_id: Optional override for project tenancy.

        Returns:
            (points_out, hists_out) lists of row dicts.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - We keep instrument_* and temporality explicitly to aid querying.
        # - The “hists” list includes three families in one table (Histogram,
        #   ExpHistogram, Summary) normalized into a common schema.
        # - v0.1.2: Added option session + user identity context
        # - v0.1.3: Added schema add-on parsing handling

        points_out: List[dict] = []
        hists_out: List[dict] = []

        for rm in payload.get("resourceMetrics", []) or []:
            resource = rm.get("resource") or {}
            scopes = rm.get("scopeMetrics") or rm.get("instrumentationLibraryMetrics") or []
            for sm in scopes:
                scope = sm.get("scope") or sm.get("instrumentationLibrary") or {}
                base = self._resource_scope_base(project_id, resource, scope)
                rattrs = base.get("resource_attrs_json", {})  # dict

                for m in sm.get("metrics", []) or []:
                    name = m.get("name", "") or ""
                    unit = m.get("unit", "") or ""

                    if "gauge" in m and m["gauge"]:
                        data = m["gauge"].get("dataPoints", []) or []
                        for dp in data:
                            points_out.append(self._point_row(base, rattrs, name, unit, "Gauge", dp, aggregation_temporality="UNSPECIFIED", is_monotonic=False))

                    if "sum" in m and m["sum"]:
                        summ = m["sum"]
                        data = summ.get("dataPoints", []) or []
                        temporality = summ.get("aggregationTemporality", "UNSPECIFIED")
                        is_mono = bool(summ.get("isMonotonic", False))
                        for dp in data:
                            points_out.append(self._point_row(base, rattrs, name, unit, "Sum", dp, aggregation_temporality=temporality, is_monotonic=is_mono))

                    if "histogram" in m and m["histogram"]:
                        hist = m["histogram"]
                        data = hist.get("dataPoints", []) or []
                        temporality = hist.get("aggregationTemporality", "UNSPECIFIED")
                        for dp in data:
                            hists_out.append(self._hist_row(base, rattrs, name, unit, "Histogram", dp, aggregation_temporality=temporality))

                    if "exponentialHistogram" in m and m["exponentialHistogram"]:
                        eh = m["exponentialHistogram"]
                        data = eh.get("dataPoints", []) or []
                        temporality = eh.get("aggregationTemporality", "UNSPECIFIED")
                        for dp in data:
                            hists_out.append(self._exphist_row(base, rattrs, name, unit, "ExpHistogram", dp, aggregation_temporality=temporality))

                    if "summary" in m and m["summary"]:
                        summ = m["summary"]
                        data = summ.get("dataPoints", []) or []
                        for dp in data:
                            hists_out.append(self._summary_row(base, rattrs, name, unit, "Summary", dp, aggregation_temporality="UNSPECIFIED"))

        return points_out, hists_out
    
    def _point_row(self, base: Dict[str, Any], rattrs: Dict[str, Any], name: str, unit: str, itype: str, dp: Dict[str, Any], *, aggregation_temporality: str, is_monotonic: bool) -> Dict[str, Any]:
        """
        Build one METRIC_POINT row (Gauge/Sum).

        Args:
            base: Resource/Scope base dict from `_resource_scope_base`.
            rattrs: Resource attributes dict (for identity fallbacks).
            name: Instrument name.
            unit: Semantic unit string (may be empty).
            itype: "Gauge" | "Sum".
            dp:    Data point dict (contains value/time/attrs/exemplars).
            aggregation_temporality: 'DELTA' | 'CUMULATIVE' | 'UNSPECIFIED'.
            is_monotonic: For Sums, whether counter is monotonic.

        Returns:
            Row dict with instrument metadata, timestamps, numeric value,
            attrs (point_attrs_json), and exemplars_json.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Value resolution handles asDouble/asInt and nested {'doubleValue','intValue'}.
        # - event_ts/date derived from time_unix_nano downstream by schema.
        # - Also handles when some exporters nest numbers inside 'value': {'doubleValue': ..}
        # - event_ts/date are computed downstream from time_unix_nano by schema.

        val = dp.get("asDouble")
        if val is None:
            val = dp.get("asInt")
        if val is None and "value" in dp:
            val = dp["value"]
        if isinstance(val, dict):
            val = val.get("doubleValue", val.get("intValue"))
        value = float(val or 0.0)

        point_attrs = _attributes_to_dict(dp.get("attributes"))
        row = {
            **base,
            "instrument_name": name,
            "instrument_type": itype,
            "unit": unit,
            "aggregation_temporality": aggregation_temporality,
            "is_monotonic": bool(is_monotonic),
            "time_unix_nano": int(dp.get("timeUnixNano", 0) or 0),
            "start_time_unix_nano": int(dp.get("startTimeUnixNano", 0) or 0),
            "value": value,
            "point_attrs_json": point_attrs,
            "exemplars_json": self._exemplars(dp.get("exemplars")),
        }
        ident = self._extract_identity(point_attrs, rattrs)
        if ident:
            row.update(ident)

        # NEW in v0.1.3 — apply enabled schema add-ons (metrics_points)
        self._apply_addons_to_row("metrics_points", row, point_attrs, rattrs)
        return row

    def _hist_row(self, base: Dict[str, Any], rattrs: Dict[str, Any], name: str, unit: str, itype: str, dp: Dict[str, Any], *, aggregation_temporality: str) -> Dict[str, Any]:
        """
        Build one METRIC_HIST row for explicit-bucket Histograms.

        Args:
            base, name, unit, itype: See `_point_row`.
            rattrs: Resource attributes dict (for identity fallbacks).
            dp: Data point with explicitBounds, bucketCounts, count, sum, attrs, exemplars.
            aggregation_temporality: 'DELTA' | 'CUMULATIVE' | 'UNSPECIFIED'.

        Returns:
            Row dict including bounds_json, counts_json, count, sum, timestamps,
            attrs (point_attrs_json), and exemplars_json.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - min/max are set to 0.0 placeholders (kept for schema stability).
        # - bounds_json/counts_json stay as Python lists; Producer serializes.

        bounds = dp.get("explicitBounds", []) or []
        counts = dp.get("bucketCounts", []) or []
        point_attrs = _attributes_to_dict(dp.get("attributes"))

        row = {
            **base,
            "instrument_name": name,
            "instrument_type": itype,
            "unit": unit,
            "aggregation_temporality": aggregation_temporality,
            "time_unix_nano": int(dp.get("timeUnixNano", 0) or 0),
            "start_time_unix_nano": int(dp.get("startTimeUnixNano", 0) or 0),
            "count": int(dp.get("count", 0) or 0),
            "sum": float(dp.get("sum", 0.0) or 0.0),
            "min": float(dp.get("min", 0.0) or 0.0) if "min" in dp else 0.0,
            "max": float(dp.get("max", 0.0) or 0.0) if "max" in dp else 0.0,
            "bounds_json": bounds,
            "counts_json": counts,
            "exp_zero_count": 0,
            "exp_scale": 0,
            "exp_positive_json": {},
            "exp_negative_json": {},
            "quantiles_json": [],
            "point_attrs_json": point_attrs,
            "exemplars_json": self._exemplars(dp.get("exemplars")),
        }
        ident = self._extract_identity(point_attrs, rattrs)
        if ident:
            row.update(ident)
        
        # NEW in v0.1.3 — apply enabled schema add-ons (metrics_hist)
        self._apply_addons_to_row("metrics_hist", row, point_attrs, rattrs)

        return row

    def _exphist_row(self, base: Dict[str, Any], rattrs: Dict[str, Any], name: str, unit: str, itype: str, dp: Dict[str, Any], *, aggregation_temporality: str) -> Dict[str, Any]:
        """
        Build one METRIC_HIST row for ExponentialHistograms.

        Args:
            base, name, unit, itype: See `_point_row`.
            rattrs: Resource attributes dict (for identity fallbacks).
            dp: Data point with scale, zeroCount, positive/negative buckets, attrs, exemplars.

            aggregation_temporality: 'DELTA' | 'CUMULATIVE' | 'UNSPECIFIED'.

        Returns:
            Row dict including exp_scale, exp_zero_count, exp_positive_json,
            exp_negative_json, count, sum, timestamps, attrs, exemplars_json.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - positive/negative buckets are preserved as dicts (Producer serializes).

        pos = dp.get("positive") or {}
        neg = dp.get("negative") or {}
        point_attrs = _attributes_to_dict(dp.get("attributes"))

        row = {
            **base,
            "instrument_name": name,
            "instrument_type": itype,
            "unit": unit,
            "aggregation_temporality": aggregation_temporality,
            "time_unix_nano": int(dp.get("timeUnixNano", 0) or 0),
            "start_time_unix_nano": int(dp.get("startTimeUnixNano", 0) or 0),
            "count": int(dp.get("count", 0) or 0),
            "sum": float(dp.get("sum", 0.0) or 0.0),
            "min": 0.0, "max": 0.0,  
            "bounds_json": [], "counts_json": [],
            "exp_zero_count": int(dp.get("zeroCount", 0) or 0),
            "exp_scale": int(dp.get("scale", 0) or 0),
            "exp_positive_json": {"offset": pos.get("offset", 0), "bucketCounts": pos.get("bucketCounts", []) or []},
            "exp_negative_json": {"offset": neg.get("offset", 0), "bucketCounts": neg.get("bucketCounts", []) or []},
            "quantiles_json": [],
            "point_attrs_json": point_attrs,
            "exemplars_json": self._exemplars(dp.get("exemplars")),
        }
        ident = self._extract_identity(point_attrs, rattrs)
        if ident:
            row.update(ident)
        
        # NEW in v0.1.3 — apply enabled schema add-ons (metrics_hist)
        self._apply_addons_to_row("metrics_hist", row, point_attrs, rattrs)

        return row

    def _summary_row(self, base: Dict[str, Any], rattrs: Dict[str, Any], name: str, unit: str, itype: str, dp: Dict[str, Any], *, aggregation_temporality: str) -> Dict[str, Any]:
        """
        Build one METRIC_HIST row for Summary metrics.
        """
        qv = []
        for it in dp.get("quantileValues", []) or []:
            qv.append({"q": float(it.get("quantile", 0.0) or 0.0), "v": float(it.get("value", 0.0) or 0.0)})
        point_attrs = _attributes_to_dict(dp.get("attributes"))

        row = {
            **base,
            "instrument_name": name,
            "instrument_type": itype,
            "unit": unit,
            "aggregation_temporality": aggregation_temporality,
            "time_unix_nano": int(dp.get("timeUnixNano", 0) or 0),
            "start_time_unix_nano": int(dp.get("startTimeUnixNano", 0) or 0),
            "count": int(dp.get("count", 0) or 0),
            "sum": float(dp.get("sum", 0.0) or 0.0),
            "min": 0.0, "max": 0.0,
            "bounds_json": [], "counts_json": [],
            "exp_zero_count": 0, "exp_scale": 0,
            "exp_positive_json": {}, "exp_negative_json": {},
            "quantiles_json": qv,
            "point_attrs_json": point_attrs,
            "exemplars_json": self._exemplars(dp.get("exemplars")),
        }
        ident = self._extract_identity(point_attrs, rattrs)
        if ident:
            row.update(ident)
        
        # NEW in v0.1.3 — apply enabled schema add-ons (metrics_hist)
        self._apply_addons_to_row("metrics_hist", row, point_attrs, rattrs)
        return row

    def _exemplars(self, exs: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Normalize exemplars list for both points and hists.

        Args:
            exs: List of exemplar dicts, possibly carrying asDouble/asInt/value,
                timeUnixNano, traceId/spanId, filteredAttributes.

        Returns:
            List of compact dicts:
            {time_unix_nano, value, trace_id, span_id, filtered_attrs}
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Handles exporters that nest value under {'doubleValue','intValue'}.
        # - IDs normalized via _lower_hex_or_empty. Attributes normalized via _attributes_to_dict.

        out: List[Dict[str, Any]] = []
        if not exs:
            return out
        for e in exs:
            val = e.get("asDouble")
            if val is None:
                val = e.get("asInt")
            if isinstance(val, dict):
                val = val.get("doubleValue", val.get("intValue"))
            out.append({
                "time_unix_nano": int(e.get("timeUnixNano", 0) or 0),
                "value": float(val or 0.0),
                "trace_id": _lower_hex_or_empty(e.get("traceId")),
                "span_id": _lower_hex_or_empty(e.get("spanId")),
                "filtered_attrs": _attributes_to_dict(e.get("filteredAttributes")),
            })
        return out

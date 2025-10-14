from __future__ import annotations
import sys, logging, json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Any, Dict, TypedDict
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

_initialized = False
_resource: Optional[Resource] = None

# числовые уровни OTel
_OTEL_SEVERITY = {
    'NOTSET': 0, 'TRACE': 1, 'DEBUG': 5, 'INFO': 9,
    'WARN': 13, 'WARNING': 13, 'ERROR': 17, 'FATAL': 21, 'CRITICAL': 21,
}

@dataclass
class OtelLogConfig:
    service_name: str
    environment: str = "production"
    service_version: Optional[str] = None
    json_stdout: bool = True
    add_stderr_for_warnings: bool = False
    logger_name: str = ""
    level: int = logging.INFO

class LogAttrs(TypedDict, total=False):
    # HTTP
    http_request_method: str
    http_route: str
    http_response_status_code: int
    url_path: str
    url_scheme: str
    server_address: str
    server_port: int
    client_address: str
    user_agent_original: str

    # DB
    db_system: str
    db_operation: str
    db_name: str
    net_peer_name: str
    net_peer_port: int

    # Exception
    exception_type: str
    exception_message: str
    exception_stacktrace: str

    # Domain / misc
    log_record_uid: str
    user_id: str
    session_id: str

# mapping именованных аргументов -> OTel ключи
_ATTR_MAPPING = {
    "http_request_method": "http.request.method",
    "http_route": "http.route",
    "http_response_status_code": "http.response.status_code",
    "url_path": "url.path",
    "url_scheme": "url.scheme",
    "server_address": "server.address",
    "server_port": "server.port",
    "client_address": "client.address",
    "user_agent_original": "user_agent.original",
    "db_system": "db.system",
    "db_operation": "db.operation",
    "db_name": "db.name",
    "net_peer_name": "net.peer.name",
    "net_peer_port": "net.peer.port",
    "exception_type": "exception.type",
    "exception_message": "exception.message",
    "exception_stacktrace": "exception.stacktrace",
    "log_record_uid": "log.record.uid",
    "user_id": "user.id",
    "session_id": "session.id"
}

def _filter_attrs(attrs: LogAttrs) -> dict:
    """Фильтруем только разрешённые ключи и переводим в OTel-имена"""
    return { _ATTR_MAPPING[k]: v for k, v in attrs.items() if k in _ATTR_MAPPING }

def _rfc3339_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace("+00:00","Z")

def _format_trace_id(tid: int) -> str:
    return f"{tid:032x}" if tid else ""

def _format_span_id(sid: int) -> str:
    return f"{sid:016x}" if sid else ""

class _JsonOtelFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: Dict[str, Any] = {
            "timestamp": _rfc3339_now(),
            "severity_text": record.levelname,
            "severity_number": _OTEL_SEVERITY.get(record.levelname, 0),
            "body": record.getMessage(),
        }

        if _resource:
            log["resource"] = dict(_resource.attributes)

        attrs: Dict[str, Any] = getattr(record, "attrs", {})
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            ctx = span.get_span_context()
            attrs.setdefault("trace_id", _format_trace_id(ctx.trace_id))
            attrs.setdefault("span_id", _format_span_id(ctx.span_id))

        if attrs:
            log["attributes"] = attrs

        return json.dumps(log, ensure_ascii=False, separators=(',', ':'))

def init(
    service_name: str,
    environment: str = "production",
    service_version: Optional[str] = None,
    json_stdout: bool = True,
    add_stderr_for_warnings: bool = False,
    logger_name: str = "",
    level: int = logging.INFO,
) -> None:
    global _initialized, _resource
    if _initialized: return

    attrs = {"service.name": service_name, "deployment.environment": environment}
    if service_version: attrs["service.version"] = service_version
    _resource = Resource.create(attrs)

    trace.set_tracer_provider(TracerProvider(resource=_resource))

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    fmt = _JsonOtelFormatter()

    if json_stdout:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(fmt)
        logger.addHandler(h)

    if add_stderr_for_warnings:
        h2 = logging.StreamHandler(sys.stderr)
        h2.setLevel(logging.WARNING)
        h2.setFormatter(fmt)
        logger.addHandler(h2)

    _initialized = True

class Logger:
    def __init__(self, name: str = ""):
        self._logger = logging.getLogger(name)

    def info(self, msg: str, **attrs: Any):

        self._logger.info(msg, extra={"attrs": _filter_attrs(attrs)})

    def error(self, msg: str, **attrs: Any):
        self._logger.error(msg, extra={"attrs": _filter_attrs(attrs)})

    def warning(self, msg: str, **attrs: Any):
        self._logger.warning(msg, extra={"attrs": _filter_attrs(attrs)})

    def debug(self, msg: str, **attrs: Any):
        self._logger.debug(msg, extra={"attrs": _filter_attrs(attrs)})

    def exception(self, msg: str, **attrs: Any):
        self._logger.exception(msg, extra={"attrs": _filter_attrs(attrs)})

def get_logger(name: str = "") -> Logger:
    return Logger(name)

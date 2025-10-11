"""Internal helpers for converting between protobuf and domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp

from .pb import analytics_pb2
from .types import (
    Anomaly,
    ErrorInfo,
    MetricUpdate,
    Pagination,
    ServerInfo,
    ServerMetrics,
    SessionInfo,
    TimeRange,
    TimelinePoint,
    ToolMetrics,
)

def to_pb_time_range(time_range: Optional[TimeRange]) -> Optional[analytics_pb2.TimeRange]:
    if time_range is None:
        return None
    return analytics_pb2.TimeRange(datetime_to_timestamp(time_range.start), to=datetime_to_timestamp(time_range.end))



def from_pb_time_range(message: Optional[analytics_pb2.TimeRange]) -> TimeRange:
    if message is None:
        return TimeRange(start=datetime.min, end=datetime.min)
    return TimeRange(
        start=_timestamp_to_datetime(message.from_),
        end=_timestamp_to_datetime(message.to),
    )


def from_pb_server_info(message: analytics_pb2.ServerInfo) -> ServerInfo:
    return ServerInfo(
        id=message.id,
        name=message.name,
        description=message.description,
        version=message.version,
        first_seen=_timestamp_to_datetime(message.first_seen),
        last_seen=_timestamp_to_datetime(message.last_seen),
        metadata=_struct_to_dict(message.metadata),
    )


def from_pb_server_metrics(message: analytics_pb2.GetServerMetricsResponse) -> ServerMetrics:
    timeline = [from_pb_timeline_point(point) for point in message.timeline]
    return ServerMetrics(
        server_id=message.server_id,
        time_range=from_pb_time_range(message.time_range),
        total_calls=message.total_calls,
        success_rate=message.success_rate,
        error_rate=message.error_rate,
        avg_latency_ms=message.avg_latency_ms,
        p95_latency_ms=message.p95_latency_ms,
        p99_latency_ms=message.p99_latency_ms,
        active_sessions=message.active_sessions,
        unique_tools_used=message.unique_tools_used,
        timeline=timeline,
    )


def from_pb_timeline_point(message: analytics_pb2.TimelinePoint) -> TimelinePoint:
    return TimelinePoint(
        timestamp=_timestamp_to_datetime(message.timestamp),
        calls=message.calls,
        errors=message.errors,
        avg_latency_ms=message.avg_latency_ms,
    )


def from_pb_tool_metrics(message: analytics_pb2.ToolMetrics) -> ToolMetrics:
    last_called = _optional_timestamp_to_datetime(message.last_called)
    last_error = _optional_timestamp_to_datetime(message.last_error)
    return ToolMetrics(
        name=message.name,
        call_count=message.call_count,
        success_count=message.success_count,
        error_count=message.error_count,
        success_rate=message.success_rate,
        avg_duration_ms=message.avg_duration_ms,
        p50_duration_ms=message.p50_duration_ms,
        p95_duration_ms=message.p95_duration_ms,
        p99_duration_ms=message.p99_duration_ms,
        last_called=last_called,
        last_error=last_error,
    )


def from_pb_error_info(message: analytics_pb2.ErrorInfo) -> ErrorInfo:
    session_id = message.session_id or None
    return ErrorInfo(
        id=message.id,
        timestamp=_timestamp_to_datetime(message.timestamp),
        tool_name=message.tool_name,
        error_message=message.error_message,
        error_type=message.error_type,
        session_id=session_id,
        duration_ms=message.duration_ms,
        parameters=_struct_to_dict(message.parameters),
    )


def from_pb_session_info(message: analytics_pb2.SessionInfo) -> SessionInfo:
    end_time = _optional_timestamp_to_datetime(message.end_time)
    return SessionInfo(
        id=message.id,
        start_time=_timestamp_to_datetime(message.start_time),
        end_time=end_time,
        duration_ms=message.duration_ms,
        tool_call_count=message.tool_call_count,
        resource_access_count=message.resource_access_count,
        status=message.status,
        client_name=message.client_name,
        client_version=message.client_version,
        protocol_version=message.protocol_version,
        last_activity=_timestamp_to_datetime(message.last_activity),
    )


def from_pb_anomaly(message: analytics_pb2.Anomaly) -> Anomaly:
    return Anomaly(
        type=message.type,
        tool_name=message.tool_name,
        detected_at=_timestamp_to_datetime(message.detected_at),
        severity=message.severity,
        description=message.description,
        baseline_value=message.baseline_value,
        current_value=message.current_value,
        confidence=message.confidence,
    )


def from_pb_metric_update(message: analytics_pb2.MetricUpdate) -> MetricUpdate:
    return MetricUpdate(
        type=message.type,
        server_id=message.server_id,
        timestamp=_timestamp_to_datetime(message.timestamp),
        data=_struct_to_dict(message.data),
    )


def from_pb_pagination(message: Optional[analytics_pb2.Pagination]) -> Pagination:
    if message is None:
        return Pagination(total=0, limit=0, offset=0)
    return Pagination(
        total=message.total,
        limit=message.limit,
        offset=message.offset,
    )


def _struct_to_dict(struct: Optional[Struct]) -> Dict[str, Any]:
    if struct is None:
        return {}
    return MessageToDict(struct, preserving_proto_field_name=True)


def _timestamp_to_datetime(timestamp: Timestamp) -> datetime:
    return timestamp.ToDatetime().replace(tzinfo=None)


def _optional_timestamp_to_datetime(timestamp: Optional[Timestamp]) -> Optional[datetime]:
    if timestamp is None:
        return None
    return _timestamp_to_datetime(timestamp)


def datetime_to_timestamp(value: datetime) -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(value)
    return ts

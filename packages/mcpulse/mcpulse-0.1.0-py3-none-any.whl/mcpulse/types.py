"""Domain models for the MCPulse Python SDK."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class TimeRange:
    """Represents a time interval."""

    start: datetime
    end: datetime


@dataclass
class Pagination:
    total: int
    limit: int
    offset: int


@dataclass
class ServerInfo:
    id: str
    name: str
    description: str
    version: str
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any]


@dataclass
class TimelinePoint:
    timestamp: datetime
    calls: int
    errors: int
    avg_latency_ms: float


@dataclass
class ServerMetrics:
    server_id: str
    time_range: TimeRange
    total_calls: int
    success_rate: float
    error_rate: float
    avg_latency_ms: float
    p95_latency_ms: int
    p99_latency_ms: int
    active_sessions: int
    unique_tools_used: int
    timeline: List[TimelinePoint]


@dataclass
class ToolMetrics:
    name: str
    call_count: int
    success_count: int
    error_count: int
    success_rate: float
    avg_duration_ms: float
    p50_duration_ms: int
    p95_duration_ms: int
    p99_duration_ms: int
    last_called: Optional[datetime]
    last_error: Optional[datetime]


@dataclass
class ErrorInfo:
    id: str
    timestamp: datetime
    tool_name: str
    error_message: str
    error_type: str
    session_id: Optional[str]
    duration_ms: int
    parameters: Dict[str, Any]


@dataclass
class SessionInfo:
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: int
    tool_call_count: int
    resource_access_count: int
    status: str
    client_name: str
    client_version: str
    protocol_version: str
    last_activity: datetime


@dataclass
class Anomaly:
    type: str
    tool_name: str
    detected_at: datetime
    severity: str
    description: str
    baseline_value: float
    current_value: float
    confidence: float


@dataclass
class SessionsQuery:
    server_id: str
    from_time: Optional[datetime] = None
    active_only: bool = False
    limit: int = 20
    offset: int = 0


@dataclass
class MetricUpdate:
    type: str
    server_id: str
    timestamp: datetime
    data: Dict[str, Any]

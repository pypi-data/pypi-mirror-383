import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, List, Optional, Sequence, Union
from urllib import request as urllib_request

import grpc  # type: ignore
from google.protobuf import struct_pb2, timestamp_pb2  # type: ignore

from .pb import analytics_pb2, analytics_pb2_grpc
from .types import MetricUpdate
from ._convert import from_pb_metric_update

ISO_FORMATS = (
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
)


@dataclass
class IngestError:
    index: int
    reason: str


@dataclass
class IngestResult:
    accepted: int
    rejected: int
    errors: List[IngestError]


class AnalyticsClient:
    """
    High-level client for interacting with MCPulse ingestion APIs.

    Supports both gRPC and REST transports and provides helpers for streaming.
    """

    def __init__(
        self,
        *,
        transport: str = "grpc",
        grpc_endpoint: str = "localhost:9090",
        rest_endpoint: str = "http://localhost:8080",
        api_key: str = "",
        timeout: float = 10.0,
    ) -> None:
        self.transport = transport.lower()
        self.timeout = timeout
        self.api_key = api_key
        self._grpc_channel: Optional[grpc.Channel] = None
        self._stub: Optional[analytics_pb2_grpc.AnalyticsServiceStub] = None
        self._rest_endpoint = rest_endpoint.rstrip("/")

        if self.transport == "grpc":
            self._grpc_channel = grpc.insecure_channel(grpc_endpoint)
            self._stub = analytics_pb2_grpc.AnalyticsServiceStub(self._grpc_channel)
        elif self.transport == "rest":
            pass
        else:
            raise ValueError("transport must be one of: grpc, rest")

    def close(self) -> None:
        """Close underlying resources."""
        if self._grpc_channel:
            self._grpc_channel.close()
            self._grpc_channel = None

    # --------------------------------------------------------------------- #
    # Ingestion
    # --------------------------------------------------------------------- #
    def ingest_metrics(self, metrics: Sequence[dict]) -> IngestResult:
        """Ingest a batch of tool call metrics."""
        if self.transport == "grpc":
            assert self._stub is not None
            request = analytics_pb2.IngestRequest(
                metrics=[_dict_to_pb_metric(metric) for metric in metrics]
            )
            # Add API key to metadata if configured
            metadata = []
            if self.api_key:
                metadata.append(("x-api-key", self.api_key))
            response = self._stub.IngestMetrics(request, timeout=self.timeout, metadata=metadata)
            return _pb_ingest_to_result(response)
        payload = json.dumps({"metrics": metrics}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        # Add API key to headers if configured
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        req = urllib_request.Request(
            f"{self._rest_endpoint}/api/v1/ingest",
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib_request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            errors = [
                IngestError(index=err["index"], reason=err["reason"])
                for err in data.get("errors", [])
            ]
            return IngestResult(
                accepted=data.get("accepted", 0),
                rejected=data.get("rejected", 0),
                errors=errors,
            )

    def ingest_metrics_stream(self, batches: Iterable[Sequence[dict]]) -> IngestResult:
        """Stream metrics batches over a single gRPC request."""
        if self.transport != "grpc":
            raise RuntimeError("streaming ingestion is only available over gRPC")
        assert self._stub is not None

        def generator() -> Iterator[analytics_pb2.IngestRequest]:
            for batch in batches:
                yield analytics_pb2.IngestRequest(
                    metrics=[_dict_to_pb_metric(metric) for metric in batch]
                )

        metadata = []
        if self.api_key:
            metadata.append(("x-api-key", self.api_key))
        response = self._stub.IngestMetricsStream(generator(), timeout=self.timeout, metadata=metadata)
        return _pb_ingest_to_result(response)

    # --------------------------------------------------------------------- #
    # Streaming
    # --------------------------------------------------------------------- #
    def stream_metrics(
        self,
        *,
        server_id: Optional[str] = None,
        topics: Optional[Sequence[str]] = None,
    ) -> Iterator[MetricUpdate]:
        """Stream real-time metric updates via gRPC."""
        if self.transport != "grpc":
            raise RuntimeError("metric streaming is only available over gRPC")
        assert self._stub is not None

        request = analytics_pb2.StreamMetricsRequest(
            server_id=server_id or "",
            topics=list(topics or []),
        )
        metadata = []
        if self.api_key:
            metadata.append(("x-api-key", self.api_key))
        stream = self._stub.StreamMetrics(request, timeout=self.timeout, metadata=metadata)
        for update in stream:
            yield from_pb_metric_update(update)

    def stream_metrics_async(
        self,
        callback,
        *,
        server_id: Optional[str] = None,
        topics: Optional[Sequence[str]] = None,
        poll_interval: float = 0.0,
    ) -> threading.Thread:
        """Start streaming metrics in a background thread and invoke callback per update."""

        def worker() -> None:
            try:
                for update in self.stream_metrics(server_id=server_id, topics=topics):
                    callback(update)
                    if poll_interval > 0:
                        time.sleep(poll_interval)
            except grpc.RpcError as err:  # pragma: no cover - transport errors bubble up
                callback(err)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread


# ------------------------------------------------------------------------- #
# Helpers
# ------------------------------------------------------------------------- #

def _dict_to_pb_metric(data: dict) -> analytics_pb2.ToolCallMetric:
    params_struct = None
    if "parameters" in data and isinstance(data["parameters"], dict):
        params_struct = struct_pb2.Struct()
        params_struct.update(data["parameters"])

    timestamp_proto = None
    ts_value = data.get("timestamp")
    if ts_value:
        dt = _parse_timestamp(ts_value)
        timestamp_proto = timestamp_pb2.Timestamp()
        timestamp_proto.FromDatetime(dt)

    metric = analytics_pb2.ToolCallMetric(
        id=data.get("id", ""),
        timestamp=timestamp_proto,
        server_id=data.get("server_id", ""),
        session_id=data.get("session_id", ""),
        tool_name=data.get("tool_name", ""),
        parameters=params_struct,
        duration_ms=int(data.get("duration_ms", 0)),
        status=_status_to_pb(data.get("status")),
        error_message=data.get("error_message", "") or "",
        error_type=data.get("error_type", "") or "",
        result_size=int(data.get("result_size", 0)),
        protocol_version=data.get("protocol_version", "") or "",
        client_name=data.get("client_name", "") or "",
        client_version=data.get("client_version", "") or "",
    )

    return metric


def _parse_timestamp(value: Union[str, datetime]) -> datetime:
    if isinstance(value, datetime):
        return value

    for fmt in ISO_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt
        except ValueError:
            continue

    return datetime.fromisoformat(value)


def _status_to_pb(status: Optional[str]) -> analytics_pb2.MetricStatus.ValueType:
    mapping = {
        "success": analytics_pb2.MetricStatus.METRIC_STATUS_SUCCESS,
        "error": analytics_pb2.MetricStatus.METRIC_STATUS_ERROR,
        "timeout": analytics_pb2.MetricStatus.METRIC_STATUS_TIMEOUT,
    }
    if not status:
        return analytics_pb2.MetricStatus.METRIC_STATUS_UNSPECIFIED
    return mapping.get(status.lower(), analytics_pb2.MetricStatus.METRIC_STATUS_UNSPECIFIED)


def _pb_ingest_to_result(resp: analytics_pb2.IngestResponse) -> IngestResult:
    return IngestResult(
        accepted=resp.accepted,
        rejected=resp.rejected,
        errors=[IngestError(index=err.index, reason=err.reason) for err in resp.errors],
    )


__all__ = ["AnalyticsClient", "IngestResult", "IngestError"]

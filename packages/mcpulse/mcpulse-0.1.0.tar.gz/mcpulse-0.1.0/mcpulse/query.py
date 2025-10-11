"""Query client for MCPulse analytics."""

from __future__ import annotations

from typing import Iterator, List, Optional, Tuple

import grpc

from .pb import analytics_pb2, analytics_pb2_grpc
from ._convert import (
    datetime_to_timestamp,
    from_pb_anomaly,
    from_pb_error_info,
    from_pb_metric_update,
    from_pb_pagination,
    from_pb_server_info,
    from_pb_server_metrics,
    from_pb_session_info,
    from_pb_timeline_point,
    from_pb_tool_metrics,
    to_pb_time_range,
)
from .types import (
    Anomaly,
    ErrorInfo,
    MetricUpdate,
    Pagination,
    ServerInfo,
    ServerMetrics,
    SessionInfo,
    SessionsQuery,
    TimeRange,
    TimelinePoint,
    ToolMetrics,
)


class QueryClient:
    """Client for querying MCPulse analytics.

    Provides methods to query server metrics, tool statistics, errors, and sessions.
    """

    def __init__(self, channel: grpc.Channel, api_key: Optional[str] = None):
        """Initialize the query client.

        Args:
            channel: gRPC channel to the MCPulse server
            api_key: Optional API key for authentication
        """
        self.stub = analytics_pb2_grpc.AnalyticsServiceStub(channel)
        self.api_key = api_key

    def _get_metadata(self):
        """Get metadata for authentication."""
        if self.api_key:
            return [("x-api-key", self.api_key)]
        return []

    def list_servers(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[ServerInfo], Pagination]:
        """List all registered MCP servers.

        Args:
            limit: Maximum number of servers to return
            offset: Number of servers to skip

        Returns:
            Tuple containing the server list and pagination metadata
        """
        request = analytics_pb2.ListServersRequest(limit=limit, offset=offset)
        response = self.stub.ListServers(request, metadata=self._get_metadata())
        servers = [from_pb_server_info(server) for server in response.servers]
        return servers, from_pb_pagination(response.pagination)

    def get_server(self, server_id: str) -> ServerInfo:
        """Get detailed information for a specific server.

        Args:
            server_id: ID of the server

        Returns:
            ServerInfo describing the requested server
        """
        request = analytics_pb2.GetServerRequest(server_id=server_id)
        response = self.stub.GetServer(request, metadata=self._get_metadata())
        return from_pb_server_info(response.server)

    def get_server_metrics(
        self,
        server_id: str,
        time_range: Optional[TimeRange] = None,
        interval: str = "",
    ) -> ServerMetrics:
        """Get aggregated metrics for a server.

        Args:
            server_id: ID of the server
            time_range: Optional time range for metrics
            interval: Time bucket size (e.g., "1h", "5m")

        Returns:
            ServerMetrics summarising activity for the server
        """
        request = analytics_pb2.GetServerMetricsRequest(
            server_id=server_id,
            time_range=to_pb_time_range(time_range),
            interval=interval,
        )
        response = self.stub.GetServerMetrics(request, metadata=self._get_metadata())
        return from_pb_server_metrics(response)

    def get_tools(
        self,
        server_id: str,
        time_range: Optional[TimeRange] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "",
    ) -> Tuple[List[ToolMetrics], Pagination]:
        """Get tool analytics for a server.

        Args:
            server_id: ID of the server
            time_range: Optional time range for metrics
            limit: Maximum number of tools to return
            offset: Number of tools to skip
            sort_by: Field to sort by (e.g., "call_count", "error_rate")

        Returns:
            Tuple of tool metrics and pagination metadata
        """
        request = analytics_pb2.GetToolsRequest(
            server_id=server_id,
            time_range=to_pb_time_range(time_range),
            limit=limit,
            offset=offset,
            sort_by=sort_by,
        )
        response = self.stub.GetTools(request, metadata=self._get_metadata())
        tools = [from_pb_tool_metrics(tool) for tool in response.tools]
        return tools, from_pb_pagination(response.pagination)

    def get_tool_timeline(
        self,
        server_id: str,
        tool_name: str,
        time_range: Optional[TimeRange] = None,
        interval: str = "",
    ) -> List[TimelinePoint]:
        """Get time-series data for a specific tool.

        Args:
            server_id: ID of the server
            tool_name: Name of the tool
            time_range: Optional time range for timeline
            interval: Time bucket size (e.g., "1h", "5m")

        Returns:
            A list of timeline points describing tool activity
        """
        request = analytics_pb2.GetToolTimelineRequest(
            server_id=server_id,
            tool_name=tool_name,
            time_range=to_pb_time_range(time_range),
            interval=interval,
        )
        response = self.stub.GetToolTimeline(request, metadata=self._get_metadata())
        return [from_pb_timeline_point(point) for point in response.timeline]

    def get_errors(
        self,
        server_id: str,
        time_range: Optional[TimeRange] = None,
        tool_name: str = "",
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[ErrorInfo], Pagination]:
        """Get error events for a server.

        Args:
            server_id: ID of the server
            time_range: Optional time range for errors
            tool_name: Optional filter by tool name
            limit: Maximum number of errors to return
            offset: Number of errors to skip

        Returns:
            Tuple of error entries and pagination metadata
        """
        request = analytics_pb2.GetErrorsRequest(
            server_id=server_id,
            time_range=to_pb_time_range(time_range),
            tool_name=tool_name,
            limit=limit,
            offset=offset,
        )
        response = self.stub.GetErrors(request, metadata=self._get_metadata())
        errors = [from_pb_error_info(err) for err in response.errors]
        return errors, from_pb_pagination(response.pagination)

    def get_sessions(
        self,
        query: SessionsQuery,
    ) -> Tuple[List[SessionInfo], Pagination]:
        """Get session data for a server.

        Args:
            query: SessionsQuery defining filters and pagination

        Returns:
            Tuple containing session entries and pagination metadata
        """
        from_time_pb = None
        if query.from_time is not None:
            from_time_pb = datetime_to_timestamp(query.from_time)

        request = analytics_pb2.GetSessionsRequest(
            server_id=query.server_id,
            from_time=from_time_pb,
            active_only=query.active_only,
            limit=query.limit,
            offset=query.offset,
        )
        response = self.stub.GetSessions(request, metadata=self._get_metadata())
        sessions = [from_pb_session_info(session) for session in response.sessions]
        return sessions, from_pb_pagination(response.pagination)

    def get_anomalies(
        self,
        server_id: str,
        time_range: Optional[TimeRange] = None,
        sensitivity: str = "medium",
    ) -> List[Anomaly]:
        """Get detected anomalies for a server.

        Args:
            server_id: ID of the server
            time_range: Optional time range for anomaly detection
            sensitivity: Sensitivity level ("low", "medium", "high")

        Returns:
            A list of detected anomalies
        """
        request = analytics_pb2.GetAnomaliesRequest(
            server_id=server_id,
            time_range=to_pb_time_range(time_range),
            sensitivity=sensitivity,
        )
        response = self.stub.GetAnomalies(request, metadata=self._get_metadata())
        return [from_pb_anomaly(anomaly) for anomaly in response.anomalies]

    def stream_metrics(
        self,
        server_id: str,
        topics: Optional[List[str]] = None,
    ) -> Iterator[MetricUpdate]:
        """Stream real-time metrics for a server.

        Args:
            server_id: ID of the server
            topics: Optional list of topics to subscribe to

        Yields:
            MetricUpdate objects as updates arrive
        """
        request = analytics_pb2.StreamMetricsRequest(
            server_id=server_id,
            topics=topics or [],
        )
        stream = self.stub.StreamMetrics(request, metadata=self._get_metadata())
        for update in stream:
            yield from_pb_metric_update(update)

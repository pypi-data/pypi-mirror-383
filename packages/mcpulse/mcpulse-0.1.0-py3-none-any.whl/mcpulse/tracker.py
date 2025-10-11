import asyncio
import functools
import inspect
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generator, Optional, Iterator

from .collector import Collector
from .config import Config


class AnalyticsTracker:
    """High-level tracker with decorators and context managers."""

    def __init__(self, config: Config) -> None:
        self.logger = config.get_logger("AnalyticsTracker")
        self.logger.info(f"Initializing tracker for server_id={config.server_id}")
        self.config = config
        self.collector = Collector(config)
        self._current_session: Optional[str] = None

    def flush(self) -> None:
        """Flush all buffered metrics."""
        self.collector.flush()

    def close(self) -> None:
        """Close the tracker and flush remaining metrics."""
        self.collector.close()

    def track_tool_call(self, tool_name: str, enable_param_collection: Optional[bool] = None) -> Callable:

        def decorator(func: Callable) -> Callable:
            sig = inspect.signature(func)
            is_async = asyncio.iscoroutinefunction(func)
            collect_params = (
                enable_param_collection
                if enable_param_collection is not None
                else self.config.enable_param_collection
            )

            def _bind_params(args, kwargs):
                try:
                    return dict(sig.bind_partial(*args, **kwargs).arguments)
                except Exception as e:
                    self.logger.error(f"Failed to bind parameters for tool '{tool_name}': {e}")
                    return {"args": args, "kwargs": kwargs}

            def _metric(status, start, err, params):
                return {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "server_id": self.config.server_id,
                    "tool_name": tool_name,
                    "duration_ms": int((time.monotonic() - start) * 1000),
                    "status": status,
                    **({"session_id": self._current_session} if self._current_session else {}),
                    **({"parameters": params} if collect_params and params else {}),
                    **({"error_message": str(err), "error_type": type(err).__name__} if err else {}),
                }

            if is_async:
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    start = time.monotonic()
                    params = _bind_params(args, kwargs)
                    err = None
                    status = "success"
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        err, status = e, "error"
                        self.logger.error(f"Error in tracked tool call '{tool_name}': {e}")
                        raise
                    finally:
                        metric = _metric(status, start, err, params)
                        try:
                            self.collector.collect(metric)
                        except Exception as ce:
                            self.logger.error(f"Failed to collect metric for tool '{tool_name}': {ce}")

                # Preserve the original callable signature for MCP/Pydantic
                async_wrapper.__signature__ = sig
                return async_wrapper

            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    start = time.monotonic()
                    params = _bind_params(args, kwargs)
                    err = None
                    status = "success"
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        err, status = e, "error"
                        self.logger.exception(f"Error in tracked tool call '{tool_name}': {e}")
                        raise
                    finally:
                        metric = _metric(status, start, err, params)
                        try:
                            self.collector.collect(metric)
                        except Exception as ce:
                            self.logger.error(f"Failed to collect metric for tool '{tool_name}': {ce}")

                # Preserve the original callable signature for MCP/Pydantic
                sync_wrapper.__signature__ = sig
                return sync_wrapper

        return decorator

    def track_manual(
        self,
        tool_name: str,
        duration_ms: int,
        status: str = "success",
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        result_size: Optional[int] = None,
    ) -> None:
        """Manually track a tool call with given parameters."""
        metric = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server_id": self.config.server_id,
            "tool_name": tool_name,
            "duration_ms": duration_ms,
            "status": status,
            **({"session_id": self._current_session} if self._current_session else {}),
            **({"parameters": parameters} if self.config.enable_param_collection and parameters else {}),
            **({"error_message": error_message, "error_type": error_type} if error_message or error_type else {}),
            **({"result_size": result_size} if result_size is not None else {}),
        }
        self.logger.debug(f"Manually tracking metric for tool '{tool_name}': {metric}")
        try:
            self.collector.collect(metric)
        except Exception as ce:
            self.logger.error(f"Failed to collect manual metric for tool '{tool_name}': {ce}")

    @contextmanager
    def session(self, session_id: Optional[str] = None) -> Iterator[str]:
        """Context manager to track a session."""
        previous_session = self._current_session
        self._current_session = session_id or str(uuid.uuid4())
        self.logger.info(f"Starting session: {self._current_session}")
        try:
            # >>> Yield the value you want to appear after "as"
            yield self._current_session
        finally:
            # keep current session until after flush for coherent logs/flush
            self.logger.info(f"Ending session: {self._current_session}")
            self.collector.flush()

            # restore previous
            self._current_session = previous_session
            if previous_session:
                self.logger.info(f"Resumed previous session: {previous_session}")
            else:
                self.logger.info("No previous session to resume")

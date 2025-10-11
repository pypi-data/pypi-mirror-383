import random
import threading
import time
import uuid
from datetime import datetime
from typing import List, Optional

from .client import AnalyticsClient
from .config import Config
from .sanitizer import Sanitizer


class Collector:
    """Buffered collector with automatic flushing."""

    def __init__(self, config: Config) -> None:
        config.validate()
        self.config = config
        self.logger = config.get_logger("Collector")
        self.logger.debug(f"[Collector] Initializing with transport={config.transport}, grpc_endpoint={config.grpc_endpoint}, api_key={'SET' if config.api_key else 'NOT SET'}")
        self.client = AnalyticsClient(
            transport=config.transport,
            grpc_endpoint=config.grpc_endpoint,
            rest_endpoint=config.rest_endpoint,
            api_key=config.api_key,
            timeout=config.timeout,
        )

        self.sanitizer = Sanitizer(config.sanitize_params, config.sensitive_keys)

        self._buffer: List[dict] = []
        self._buffer_lock = threading.Lock()
        self._closed = False
        self._flush_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        if config.async_mode:
            self.logger.debug(f"[Collector] Starting background flusher (flush_interval={config.flush_interval}s, buffer_size={config.buffer_size})")
            self._start_flusher()
        else:
            print(f"[Collector] Synchronous mode (buffer_size={config.buffer_size})")

    def close(self) -> None:
        """Close the collector and flush remaining metrics."""
        self.logger.debug(f"[Collector] Closing collector...")
        with self._buffer_lock:
            if self._closed:
                self.logger.debug(f"[Collector] Already closed")
                return
            self._closed = True

        # Stop background flusher
        if self._flush_thread:
            self.logger.debug(f"[Collector] Stopping background flusher...")
            self._stop_event.set()
            self._flush_thread.join(timeout=5.0)

        # Final flush
        self.logger.debug(f"[Collector] Performing final flush...")
        self.flush()
        self.client.close()
        self.logger.debug(f"[Collector] Collector closed")

    def collect(self, metric: dict) -> None:
        """Add a metric to the buffer."""
        self.logger.debug(f"[Collector] Received metric: {metric.get('tool_name', 'unknown')}")
        with self._buffer_lock:
            if self._closed:
                raise RuntimeError("collector is closed")

            # Apply sampling
            if self.config.sample_rate < 1.0 and random.random() > self.config.sample_rate:
                self.logger.debug(f"[Collector] Metric sampled out (sample_rate={self.config.sample_rate})")
                return

            # Sanitize parameters
            if self.config.sanitize_params and "parameters" in metric:
                print("[Collector] Sanitizing parameters")
                metric["parameters"] = self.sanitizer.sanitize(metric["parameters"])

            # Add protocol metadata
            if "protocol_version" not in metric or not metric["protocol_version"]:
                metric["protocol_version"] = self.config.protocol_version
            if "client_name" not in metric or not metric["client_name"]:
                metric["client_name"] = self.config.client_name
            if "client_version" not in metric or not metric["client_version"]:
                metric["client_version"] = self.config.client_version

            # Ensure ID and timestamp
            if "id" not in metric or not metric["id"]:
                metric["id"] = str(uuid.uuid4())
            if "timestamp" not in metric or not metric["timestamp"]:
                metric["timestamp"] = datetime.utcnow().isoformat() + "Z"

            # Add to buffer
            self._buffer.append(metric)
            self.logger.debug(f"[Collector] Metric added to buffer. Buffer size: {len(self._buffer)}/{self.config.buffer_size}")

            # Flush if buffer is full
            if len(self._buffer) >= self.config.buffer_size:
                self.logger.debug(f"[Collector] Buffer full, flushing...")
                self._flush_locked()

    def flush(self) -> None:
        """Flush all buffered metrics."""
        self.logger.debug(f"[Collector] flush() called")
        with self._buffer_lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        """Flush metrics (must be called with lock held)."""
        if not self._buffer:
            return

        metrics = self._buffer[:]
        self._buffer.clear()
        self.logger.debug(f"[Collector] Flushing {len(metrics)} metrics...")

        # Send with retries
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            if attempt > 0:
                backoff = self.config.retry_backoff * (2 ** (attempt - 1))
                self.logger.debug(f"[Collector] Retry attempt {attempt}/{self.config.max_retries}, backing off {backoff}s...")
                time.sleep(backoff)

            try:
                self.logger.debug(f"[Collector] Calling client.ingest_metrics with {len(metrics)} metrics...")
                self.client.ingest_metrics(metrics)
                self.logger.debug(f"[Collector] Successfully sent {len(metrics)} metrics!")
                return
            except Exception as e:
                last_error = e
                self.logger.debug(f"[Collector] Error sending metrics (attempt {attempt + 1}): {type(e).__name__}: {e}")

        if last_error:
            self.logger.error(f"[Collector] FAILED to send metrics after {self.config.max_retries + 1} attempts: {last_error}")
            # Log or handle error - for now just swallow
            pass

    def _start_flusher(self) -> None:
        """Start background flusher thread."""

        def worker() -> None:
            while not self._stop_event.is_set():
                # Use wait() instead of sleep() so we can be interrupted immediately
                if self._stop_event.wait(timeout=self.config.flush_interval):
                    # Stop event was set, exit immediately
                    break
                # Flush if there are metrics
                self.flush()

        self._flush_thread = threading.Thread(target=worker, daemon=True)
        self._flush_thread.start()

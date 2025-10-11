import logging
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Configuration for the MCPulse Python SDK."""

    # Server identification
    server_id: str

    # Authentication
    api_key: str = ""  # API key for authentication (generated from MCPulse UI)

    # Transport settings
    transport: str = "grpc"
    grpc_endpoint: str = "localhost:9090"
    rest_endpoint: str = "http://localhost:8080"

    # Collection settings
    enable_param_collection: bool = True
    async_mode: bool = True
    buffer_size: int = 100
    flush_interval: float = 2.0 # seconds
    max_batch_size: int = 1000

    # Privacy settings
    sanitize_params: bool = True
    sensitive_keys: List[str] = field(
        default_factory=lambda: [
            "password",
            "token",
            "api_key",
            "secret",
            "authorization",
            "auth",
            "apikey",
            "api-key",
            "access_token",
            "refresh_token",
            "private_key",
        ]
    )

    # Sampling
    sample_rate: float = 1.0  # 0.0 to 1.0

    # Retry settings
    max_retries: int = 3
    retry_backoff: float = 1.0  # seconds

    # Timeout
    timeout: float = 10.0  # seconds

    # Logging
    log_level: str = "INFO"

    # Protocol metadata
    protocol_version: str = "2024-11-05"
    client_name: str = "mcpulse-python"
    client_version: str = "1.0.0"

    def get_logger(self, prefix: str) -> logging.Logger:
        """Get a logger with the specified prefix."""
        logger = logging.getLogger(f"{prefix}.{self.server_id}")
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(self.log_level)
        return logger


    def validate(self) -> None:
        """Validate configuration."""
        if not self.server_id:
            raise ValueError("server_id is required")
        if not 0 <= self.sample_rate <= 1:
            raise ValueError("sample_rate must be between 0 and 1")
        if self.buffer_size <= 0:
            raise ValueError("buffer_size must be positive")
        if self.max_batch_size <= 0:
            raise ValueError("max_batch_size must be positive")
        if self.transport not in ("grpc", "rest"):
            raise ValueError("transport must be 'grpc' or 'rest'")

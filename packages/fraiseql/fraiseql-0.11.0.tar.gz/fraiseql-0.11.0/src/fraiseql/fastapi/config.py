"""Configuration for FraiseQL FastAPI integration."""

import logging
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class IntrospectionPolicy(str, Enum):
    """Policy for GraphQL schema introspection access control.

    - DISABLED: No introspection allowed for anyone
    - PUBLIC: Introspection allowed for everyone (default)
    - AUTHENTICATED: Introspection only allowed for authenticated users
    """

    DISABLED = "disabled"
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"

    def allows_introspection(self, is_authenticated: bool = False) -> bool:
        """Check if introspection is allowed based on policy and authentication status."""
        if self == IntrospectionPolicy.DISABLED:
            return False
        if self == IntrospectionPolicy.PUBLIC:
            return True
        if self == IntrospectionPolicy.AUTHENTICATED:
            return is_authenticated
        return False


def validate_postgres_url(v: Any) -> str:
    """Validate PostgreSQL URL, supporting both regular and Unix socket connections.

    Unix socket URLs have the format:
    - postgresql://user@/path/to/socket:port/database
    - postgresql://user:password@/path/to/socket:port/database

    Regular URLs have the format:
    - postgresql://user:password@host:port/database
    """
    if not isinstance(v, str):
        raise TypeError("Database URL must be a string")

    # Basic validation - must start with postgresql:// or postgres://
    if not v.startswith(("postgresql://", "postgres://")):
        raise ValueError("Database URL must start with postgresql:// or postgres://")

    # Check if this looks like a Unix socket URL (has @ followed by /)
    if "@/" in v:
        # This is a Unix socket URL, which is valid
        # Just ensure it has the basic structure
        parts = v.split("@/", 1)
        if len(parts) != 2:
            raise ValueError("Invalid Unix socket URL format")
        # Ensure there's at least a database name after the socket path
        socket_and_db = parts[1]
        if "/" not in socket_and_db:
            raise ValueError("Unix socket URL must include database name")
        return v

    # For regular URLs, try to parse with PostgresDsn
    try:
        PostgresDsn(v)
    except Exception as e:
        raise ValueError(f"Invalid PostgreSQL URL: {e}") from e
    else:
        return v


# Type alias for the validated database URL
PostgresUrl = Annotated[str, Field(description="PostgreSQL connection URL (supports Unix sockets)")]


class FraiseQLConfig(BaseSettings):
    """Configuration for FraiseQL application.

    This class defines all configuration options for a FraiseQL-powered FastAPI
    application. Configuration values can be set through environment variables,
    .env files, or directly in code.

    Environment variables should be prefixed with the app name and use uppercase
    (e.g., FRAISEQL_DATABASE_URL).

    Attributes:
        database_url: PostgreSQL connection URL with JSONB support required.
            Supports Unix domain sockets (e.g., postgresql://user@/var/run/postgresql:5432/db).
        database_pool_size: Maximum number of database connections in the pool.
        database_max_overflow: Maximum overflow connections allowed beyond pool_size.
        database_pool_timeout: Seconds to wait before timing out when acquiring connection.
        database_echo: Enable SQL query logging (use only in development).
        app_name: Application name displayed in API documentation.
        app_version: Application version string.
        environment: Current environment (development/production/testing).
        introspection_policy: Policy for GraphQL schema introspection access control.
        enable_playground: Enable GraphQL playground IDE.
        playground_tool: Which GraphQL IDE to use (graphiql or apollo-sandbox).
        max_query_depth: Maximum allowed query depth to prevent abuse.
        query_timeout: Maximum query execution time in seconds.
        auto_camel_case: Automatically convert snake_case fields to camelCase.
        enable_auth: Enable authentication and authorization.
        auth_provider: Authentication provider to use.
        auth0_domain: Auth0 tenant domain (required if using Auth0).
        auth0_api_identifier: Auth0 API identifier (required if using Auth0).
        auth0_cache_ttl: Cache TTL for Auth0 JWKS in seconds.
        cors_allow_origins: List of allowed CORS origins.
        cors_allow_credentials: Allow credentials in CORS requests.
        cors_allow_methods: Allowed HTTP methods for CORS.
        cors_allow_headers: Allowed headers for CORS requests.
        enable_metrics: Enable Prometheus metrics endpoint.
        metrics_path: URL path for metrics endpoint.
        enable_health_check: Enable health check endpoints.
        health_check_path: URL path for health check.
        enable_rate_limiting: Enable rate limiting.
        rate_limit_requests: Maximum requests per period.
        rate_limit_period: Rate limit period in seconds.
        log_level: Application log level.
        log_format: Log format (json or text).
        enable_request_logging: Log all incoming requests.
        enable_response_logging: Log all outgoing responses.
        request_id_header: Header name for request correlation ID.
        jsonb_field_limit_threshold: Field count threshold for full data column (default: 20).
        apq_storage_backend: Storage backend for APQ (memory/postgresql/redis/custom).
        apq_response_cache_ttl: Cache TTL for APQ responses in seconds.
        apq_backend_config: Backend-specific configuration options.

    Example:
        ```python
        from fraiseql.fastapi import FraiseQLConfig, create_fraiseql_app

        config = FraiseQLConfig(
            database_url="postgresql://user:pass@localhost/mydb",
            environment="production",
            enable_auth=True,
            auth_provider="auth0",
            auth0_domain="myapp.auth0.com",
            auth0_api_identifier="https://api.myapp.com"
        )

        app = create_fraiseql_app(types=[User, Post], config=config)
        ```
    """

    # Database settings
    database_url: PostgresUrl
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_echo: bool = False

    # Application settings
    app_name: str = "FraiseQL API"
    app_version: str = "1.0.0"
    environment: Literal["development", "production", "testing"] = "development"

    # GraphQL settings
    introspection_policy: IntrospectionPolicy = IntrospectionPolicy.PUBLIC
    enable_playground: bool = True
    playground_tool: Literal["graphiql", "apollo-sandbox"] = "graphiql"  # Which GraphQL IDE to use
    max_query_depth: int | None = None
    query_timeout: int = 30  # seconds
    auto_camel_case: bool = True  # Auto-convert snake_case to camelCase in GraphQL

    # Auth settings
    auth_enabled: bool = True
    auth_provider: Literal["auth0", "custom", "none"] = "none"

    # Auth0 specific settings
    auth0_domain: str | None = None
    auth0_api_identifier: str | None = None
    auth0_algorithms: list[str] = ["RS256"]

    # Development auth settings
    # Generate secure random defaults if not explicitly set
    dev_auth_username: str | None = None
    dev_auth_password: str | None = None

    @field_validator("dev_auth_username")
    @classmethod
    def generate_dev_username(cls, v: str | None) -> str:
        """Set default username if not explicitly set."""
        if v is None:
            return "admin"
        return v

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: Any) -> str:
        """Validate database URL, supporting Unix domain sockets."""
        return validate_postgres_url(v)

    # Performance settings
    cache_ttl: int = 300  # seconds
    turbo_router_cache_size: int = 1000  # Max number of queries to cache
    jsonb_field_limit_threshold: int = (
        20  # Switch to full data column when field count exceeds this
    )

    # v0.11.0: Rust-only transformation (PostgreSQL CamelForge removed)
    # All camelCase transformation is handled by Rust in raw_json_executor.py
    # This simplifies architecture and maximizes performance

    # Token revocation settings
    revocation_enabled: bool = True
    revocation_check_enabled: bool = True
    revocation_ttl: int = 86400  # 24 hours
    revocation_cleanup_interval: int = 3600  # 1 hour
    revocation_store_type: str = "memory"  # "memory" or "redis"

    # Query complexity settings
    complexity_enabled: bool = True
    complexity_max_score: int = 1000
    complexity_max_depth: int = 10
    complexity_default_list_size: int = 10
    complexity_include_in_response: bool = False
    complexity_field_multipliers: dict[str, int] = {}

    # Rate limiting settings
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000
    rate_limit_burst_size: int = 10
    rate_limit_window_type: str = "sliding"  # "sliding" or "fixed"
    rate_limit_whitelist: list[str] = []
    rate_limit_blacklist: list[str] = []

    # APQ Backend Configuration
    apq_storage_backend: Literal["memory", "postgresql", "redis", "custom"] = "memory"
    apq_cache_responses: bool = False
    apq_response_cache_ttl: int = Field(default=600, ge=0)
    apq_backend_config: dict[str, Any] = {}

    # CORS settings
    cors_enabled: bool = False  # Disabled by default to avoid conflicts with reverse proxies
    cors_origins: list[str] = []  # Empty by default, must be explicitly configured
    cors_methods: list[str] = ["GET", "POST"]
    # Sensible defaults instead of wildcard
    cors_headers: list[str] = ["Content-Type", "Authorization"]

    # Execution mode settings
    execution_mode_priority: list[str] = ["turbo", "passthrough", "normal"]
    turbo_router_auto_register: bool = False
    passthrough_complexity_limit: int = 50
    passthrough_max_depth: int = 3

    # Mode hints
    mode_hint_pattern: str = r"#\s*@mode:\s*(\w+)"

    # Unified executor settings
    include_execution_metadata: bool = False  # Include mode and timing in response
    execution_timeout_ms: int = 30000  # 30 seconds

    # TurboRouter enhanced settings
    turbo_max_complexity: int = 100  # Max complexity score for turbo caching
    turbo_max_total_weight: float = 2000.0  # Max total weight of cached queries

    # Enhanced passthrough settings
    passthrough_view_metadata_ttl: int = 3600  # 1 hour

    # Default schema settings
    default_mutation_schema: str = "public"  # Default schema for mutations when not specified
    default_query_schema: str = "public"  # Default schema for queries when not specified

    # Entity routing settings
    entity_routing: Any = None
    """Configuration for entity-aware query routing (optional)."""

    @field_validator("entity_routing", mode="before")
    @classmethod
    def validate_entity_routing(cls, v: Any) -> Any:
        """Validate entity routing configuration."""
        if v is None:
            return None

        from fraiseql.routing.config import EntityRoutingConfig

        if isinstance(v, dict):
            return EntityRoutingConfig(**v)
        if isinstance(v, EntityRoutingConfig):
            return v
        raise ValueError("entity_routing must be an EntityRoutingConfig instance or dict")

    @property
    def enable_introspection(self) -> bool:
        """Backward compatibility property for enable_introspection.

        Returns True if introspection_policy allows any introspection.
        For authenticated-only policies, this returns True to allow
        the GraphQL execution layer to handle auth checks.
        """
        return self.introspection_policy != IntrospectionPolicy.DISABLED

    @field_validator("introspection_policy")
    @classmethod
    def set_production_introspection_default(
        cls, v: IntrospectionPolicy, info
    ) -> IntrospectionPolicy:
        """Set introspection policy to DISABLED in production unless explicitly set."""
        if info.data.get("environment") == "production" and v == IntrospectionPolicy.PUBLIC:
            return IntrospectionPolicy.DISABLED
        return v

    @field_validator("enable_playground")
    @classmethod
    def playground_for_dev_only(cls, v: bool, info) -> bool:
        """Disable playground in production unless explicitly enabled."""
        if info.data.get("environment") == "production" and v is True:
            return False
        return v

    @field_validator("auth0_domain")
    @classmethod
    def validate_auth0_config(cls, v: str | None, info) -> str | None:
        """Validate Auth0 configuration when Auth0 is selected."""
        if info.data.get("auth_provider") == "auth0" and not v:
            msg = "auth0_domain is required when using Auth0 provider"
            raise ValueError(msg)
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_for_production(cls, v: list[str], info) -> list[str]:
        """Warn about insecure CORS configurations in production."""
        environment = info.data.get("environment", "development")
        cors_enabled = info.data.get("cors_enabled", False)

        if environment == "production" and cors_enabled and "*" in v:
            logger.warning(
                "⚠️  CORS is enabled with wildcard origin (*) in production environment. "
                "This is a security risk and may cause conflicts with reverse proxies. "
                "Consider disabling CORS or setting specific allowed origins."
            )

        return v

    model_config = SettingsConfigDict(
        env_prefix="FRAISEQL_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra environment variables
    )

"""
Configuration management for ayz-auth package.

Uses Pydantic settings for type-safe configuration with environment variable support.
"""

import os
from typing import Any, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from typing_extensions import Self


class AuthSettings(BaseSettings):
    """
    Configuration settings for Stytch authentication middleware.

    All settings can be provided via environment variables with the STYTCH_ prefix.
    """

    # Stytch B2B API configuration
    project_id: Optional[str] = Field(
        default=None,
        description="Stytch project ID (set via STYTCH_PROJECT_ID env var)",
    )
    secret: Optional[str] = Field(
        default=None,
        description="Stytch API secret (set via STYTCH_SECRET env var)",
    )
    environment: str = Field(
        default="test", description="Stytch environment: 'test' or 'live'"
    )

    # MongoDB configuration (optional - for entitlements and team context)
    mongodb_uri: Optional[str] = Field(
        default=None,
        description="MongoDB connection URI (set via STYTCH_MONGODB_URI env var) - optional, enables entitlements features",
    )

    # Redis configuration
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0

    # Caching configuration
    cache_ttl: int = 300  # 5 minutes default
    cache_prefix: str = "ayz_auth"

    # Logging configuration
    log_level: str = "INFO"
    log_sensitive_data: bool = False  # Never log tokens in production

    # Request configuration
    request_timeout: int = 10  # seconds
    max_retries: int = 3

    model_config = {
        "env_prefix": "STYTCH_",
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @model_validator(mode="before")
    @classmethod
    def load_environment_from_legacy_var(cls, data: Any) -> Any:
        """
        Handle backward compatibility for STYTCH_ENV -> STYTCH_ENVIRONMENT.

        This ensures both STYTCH_ENV and STYTCH_ENVIRONMENT work, with STYTCH_ENVIRONMENT
        taking precedence if both are set.
        """
        if isinstance(data, dict):
            # Check if STYTCH_ENVIRONMENT is not set but STYTCH_ENV is
            if "environment" not in data and "STYTCH_ENVIRONMENT" not in os.environ:
                legacy_env = os.getenv("STYTCH_ENV")
                if legacy_env:
                    data["environment"] = legacy_env
        return data

    @model_validator(mode="after")
    def validate_required_fields(self) -> Self:
        """
        Validate required fields and set test defaults only for pytest/CI environments.
        """
        # Only provide test defaults in actual test environments (pytest, CI)
        # NOT based on STYTCH_ENV which is just for Stytch API environment selection
        is_pytest_or_ci = (
            os.getenv("PYTEST_CURRENT_TEST") is not None
            or os.getenv("CI") is not None
            or os.getenv("GITHUB_ACTIONS") is not None
            or "pytest" in os.getenv("_", "").lower()
        )

        if is_pytest_or_ci:
            # Only set defaults for actual test runs
            if not self.project_id:
                self.project_id = "test_project_id"
            if not self.secret:
                self.secret = "test_secret_key"
        else:
            # In all other cases, require project_id and secret
            if not self.project_id:
                raise ValueError(
                    "project_id is required. Set STYTCH_PROJECT_ID environment variable."
                )
            if not self.secret:
                raise ValueError(
                    "secret is required. Set STYTCH_SECRET environment variable."
                )

        return self


# Global settings instance
settings = AuthSettings()

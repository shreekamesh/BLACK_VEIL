"""
BLACK VEIL V2 — Database Configuration
Environment-based configuration for PostgreSQL, Redis, and MongoDB connections
"""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PostgresConfig:
    """PostgreSQL connection configuration"""
    host: str = os.getenv("BV_POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("BV_POSTGRES_PORT", "5432"))
    database: str = os.getenv("BV_POSTGRES_DB", "blackveil")
    username: str = os.getenv("BV_POSTGRES_USER", "blackveil")
    password: str = os.getenv("BV_POSTGRES_PASSWORD", "blackveil")
    pool_size: int = int(os.getenv("BV_POSTGRES_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("BV_POSTGRES_MAX_OVERFLOW", "20"))
    echo: bool = os.getenv("BV_POSTGRES_ECHO", "false").lower() == "true"

    @property
    def connection_string(self) -> str:
        """Build async SQLAlchemy connection string"""
        return (
            f"postgresql+asyncpg://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    @property
    def sync_connection_string(self) -> str:
        """Build sync SQLAlchemy connection string for migrations"""
        return (
            f"postgresql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


@dataclass
class RedisConfig:
    """Redis cache configuration"""
    host: str = os.getenv("BV_REDIS_HOST", "localhost")
    port: int = int(os.getenv("BV_REDIS_PORT", "6379"))
    db: int = int(os.getenv("BV_REDIS_DB", "0"))
    password: Optional[str] = os.getenv("BV_REDIS_PASSWORD", None)
    decode_responses: bool = True

    @property
    def connection_string(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


@dataclass
class MongoDBConfig:
    """MongoDB configuration for logs"""
    host: str = os.getenv("BV_MONGO_HOST", "localhost")
    port: int = int(os.getenv("BV_MONGO_PORT", "27017"))
    database: str = os.getenv("BV_MONGO_DB", "blackveil_logs")
    username: Optional[str] = os.getenv("BV_MONGO_USER", None)
    password: Optional[str] = os.getenv("BV_MONGO_PASSWORD", None)

    @property
    def connection_string(self) -> str:
        if self.username and self.password:
            return (
                f"mongodb://{self.username}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        return f"mongodb://{self.host}:{self.port}/{self.database}"


@dataclass
class DatabaseConfig:
    """Unified database configuration"""
    postgres: PostgresConfig = field(default_factory=PostgresConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    mongodb: MongoDBConfig = field(default_factory=MongoDBConfig)


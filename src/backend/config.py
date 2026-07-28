"""
BLACK VEIL V5 - Configuration Management
Hierarchical config with Pydantic Settings, YAML files, and env var overrides
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings
import yaml
import os
from pathlib import Path


class DatabaseConfig(BaseModel):
    """Base database configuration"""
    host: str = "localhost"
    port: int = 5432
    username: str = "blackveil"
    password: SecretStr = SecretStr("blackveil")
    database: str = "black_veil"
    pool_size: int = 10
    max_overflow: int = 5
    pool_timeout: int = 30
    pool_recycle: int = 3600


class PostgresConfig(DatabaseConfig):
    """PostgreSQL configuration"""
    pass


class MongoConfig(BaseModel):
    """MongoDB configuration"""
    host: str = "localhost"
    port: int = 27017
    username: str = "blackveil"
    password: SecretStr = SecretStr("blackveil")
    database: str = "black_veil"
    max_pool_size: int = 100
    min_pool_size: int = 10
    max_idle_time_ms: int = 30000


class Neo4jConfig(BaseModel):
    """Neo4j configuration"""
    host: str = "localhost"
    port: int = 7687
    username: str = "neo4j"
    password: SecretStr = SecretStr("blackveil")
    database: str = "black_veil"
    max_connection_lifetime: int = 3600
    max_connection_pool_size: int = 100


class RedisConfig(BaseModel):
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[SecretStr] = None
    db: int = 0
    max_connections: int = 100
    socket_timeout: int = 5
    socket_connect_timeout: int = 5


class MinioConfig(BaseModel):
    """MinIO configuration"""
    host: str = "localhost"
    port: int = 9000
    access_key: str = "blackveil"
    secret_key: SecretStr = SecretStr("blackveil123")
    bucket: str = "black-veil"
    secure: bool = False


class KafkaConfig(BaseModel):
    """Kafka configuration"""
    bootstrap_servers: List[str] = ["localhost:9092"]
    group_id: str = "black-veil-group"
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False
    max_poll_records: int = 500


class RabbitMQConfig(BaseModel):
    """RabbitMQ configuration"""
    host: str = "localhost"
    port: int = 5672
    username: str = "blackveil"
    password: SecretStr = SecretStr("blackveil")
    vhost: str = "/"


class CeleryConfig(BaseModel):
    """Celery configuration"""
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/1"
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: List[str] = ["json"]
    timezone: str = "UTC"
    enable_utc: bool = True
    task_track_started: bool = True
    task_time_limit: int = 3600
    task_soft_time_limit: int = 3000


class JWTConfig(BaseModel):
    """JWT configuration"""
    secret_key: SecretStr = SecretStr("change-me-in-production-use-vault")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


class SecurityConfig(BaseModel):
    """Security configuration"""
    jwt: JWTConfig = JWTConfig()
    password: Dict[str, Any] = {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digits": True,
        "require_special": True,
    }
    rate_limiting: Dict[str, Any] = {
        "enabled": True,
        "requests_per_minute": 100,
        "requests_per_hour": 1000,
        "burst_multiplier": 2,
    }


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"
    handlers: List[str] = ["console", "file"]
    file: Optional[Dict[str, Any]] = None
    loki: Optional[Dict[str, Any]] = None


class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    prometheus: Dict[str, Any] = {"enabled": True, "port": 9090, "path": "/metrics"}
    grafana: Dict[str, Any] = {"enabled": True, "url": "http://grafana:3000"}
    jaeger: Dict[str, Any] = {"enabled": True, "agent_host": "jaeger-agent", "agent_port": 6831, "service_name": "black-veil-backend"}


class AIConfig(BaseModel):
    """AI configuration"""
    models_path: str = "/models"
    cache_size: int = 1000
    cache_ttl: int = 300
    ensemble_weights: Dict[str, float] = {"cnn": 0.35, "dnn": 0.30, "xgboost": 0.35}
    confidence_threshold: float = 0.7
    max_parallel_models: int = 4


class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = "BLACK VEIL V5"
    version: str = "5.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    max_requests: int = 10000
    timeout_seconds: int = 60
    cors_origins: List[str] = ["http://localhost:3000"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]

    # Nested configs
    security: SecurityConfig = SecurityConfig()
    postgres: PostgresConfig = PostgresConfig()
    mongodb: MongoConfig = MongoConfig()
    neo4j: Neo4jConfig = Neo4jConfig()
    redis: RedisConfig = RedisConfig()
    minio: MinioConfig = MinioConfig()
    kafka: KafkaConfig = KafkaConfig()
    rabbitmq: RabbitMQConfig = RabbitMQConfig()
    celery: CeleryConfig = CeleryConfig()
    ai: AIConfig = AIConfig()
    logging: LoggingConfig = LoggingConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    openapi: Dict[str, Any] = {
        "title": "BLACK VEIL V5 API",
        "version": "5.0.0",
        "description": "Cognitive Autonomous Cyber Defense Organism",
        "contact": {"name": "BLACK VEIL Team", "email": "support@black-veil.io"},
        "license": {"name": "Proprietary"},
        "servers": [
            {"url": "https://api.black-veil.io/api/v1", "description": "Production"},
            {"url": "http://localhost:8000/api/v1", "description": "Local Development"},
        ],
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        @classmethod
        def parse_config(cls, config_file: str) -> Dict[str, Any]:
            """Parse YAML configuration file with env var expansion"""
            config_path = Path(config_file)
            if not config_path.exists():
                return {}
            with open(config_path) as f:
                config = yaml.safe_load(f)
            return cls._expand_env_vars(config) if config else {}

        @staticmethod
        def _expand_env_vars(config: Any) -> Any:
            """Recursively expand ${ENV_VAR} placeholders"""
            if isinstance(config, dict):
                return {k: Settings.Config._expand_env_vars(v) for k, v in config.items()}
            elif isinstance(config, list):
                return [Settings.Config._expand_env_vars(item) for item in config]
            elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
                return os.environ.get(config[2:-1], config)
            return config


def load_settings() -> Settings:
    """Load settings from configuration files with layered overrides"""
    env = os.environ.get("ENVIRONMENT", "development")

    # Layered config loading (each layer overrides previous)
    config: Dict[str, Any] = {}
    for layer in ["config/default.yaml", f"config/{env}.yaml", "config/local.yaml"]:
        try:
            layer_config = Settings.Config.parse_config(layer)
            config.update(layer_config)
        except FileNotFoundError:
            pass

    # Create settings from merged config + env overrides
    settings = Settings(**config)

    # Environment variable overrides (uppercase matches setting fields)
    for field in settings.model_dump().keys():
        env_value = os.environ.get(field.upper())
        if env_value is not None:
            setattr(settings, field, env_value)

    return settings


# Global singleton
settings = load_settings()


# Convenience variables for direct import
BUILD_ID = os.environ.get("BUILD_ID", "dev")
API_PREFIX = os.environ.get("API_PREFIX", "/api/v1")
APP_NAME = settings.app_name
APP_VERSION = settings.version
ENVIRONMENT = settings.environment
DEBUG = settings.debug
CORS_ORIGINS = settings.cors_origins
ALLOWED_HOSTS = settings.allowed_hosts

# Auth/JWT
AUTH_SECRET_KEY = settings.security.jwt.secret_key.get_secret_value()
AUTH_ALGORITHM = settings.security.jwt.algorithm
AUTH_TOKEN_TYPE = "access"
JWT_SECRET_KEY = AUTH_SECRET_KEY
JWT_ALGORITHM = AUTH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.security.jwt.refresh_token_expire_days
API_KEY_PREFIX = "bv"

# Rate Limiting
RATE_LIMIT_ENABLED = settings.security.rate_limiting.get("enabled", True)
RATE_LIMIT_REQUESTS = settings.security.rate_limiting.get("requests_per_minute", 100)
RATE_LIMIT_WINDOW = 60

POSTGRES_HOST = settings.postgres.host
POSTGRES_PORT = settings.postgres.port
POSTGRES_USER = settings.postgres.username
POSTGRES_PASSWORD = settings.postgres.password.get_secret_value()
POSTGRES_DATABASE = settings.postgres.database
POSTGRES_POOL_SIZE = settings.postgres.pool_size
POSTGRES_MAX_OVERFLOW = settings.postgres.max_overflow
POSTGRES_POOL_TIMEOUT = settings.postgres.pool_timeout
POSTGRES_POOL_RECYCLE = settings.postgres.pool_recycle
MONGO_HOST = settings.mongodb.host
MONGO_PORT = settings.mongodb.port
MONGO_USER = settings.mongodb.username
MONGO_PASSWORD = settings.mongodb.password.get_secret_value()
MONGO_DATABASE = settings.mongodb.database
MONGO_MAX_POOL_SIZE = settings.mongodb.max_pool_size
MONGO_MIN_POOL_SIZE = settings.mongodb.min_pool_size
MONGO_MAX_IDLE_TIME_MS = settings.mongodb.max_idle_time_ms
NEO4J_HOST = settings.neo4j.host
NEO4J_PORT = settings.neo4j.port
NEO4J_USER = settings.neo4j.username
NEO4J_PASSWORD = settings.neo4j.password.get_secret_value()
NEO4J_DATABASE = settings.neo4j.database
NEO4J_MAX_CONNECTION_LIFETIME = settings.neo4j.max_connection_lifetime
NEO4J_MAX_CONNECTION_POOL_SIZE = settings.neo4j.max_connection_pool_size
REDIS_HOST = settings.redis.host
REDIS_PORT = settings.redis.port
REDIS_PASSWORD = settings.redis.password.get_secret_value() if settings.redis.password else ""
REDIS_DB = settings.redis.db
REDIS_MAX_CONNECTIONS = settings.redis.max_connections
REDIS_SOCKET_TIMEOUT = settings.redis.socket_timeout
REDIS_SOCKET_CONNECT_TIMEOUT = settings.redis.socket_connect_timeout

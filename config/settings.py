"""
BLACK VEIL V5 — Complete Configuration Management
All settings with environment variable overrides and YAML config file support
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings


# ── Database Configurations ────────────────────────────────────

class PostgresConfig(BaseModel):
    """PostgreSQL connection configuration"""
    host: str = Field(default="localhost", alias="BV_POSTGRES_HOST")
    port: int = Field(default=5432, alias="BV_POSTGRES_PORT")
    username: str = Field(default="blackveil", alias="BV_POSTGRES_USER")
    password: SecretStr = Field(default="blackveil", alias="BV_POSTGRES_PASSWORD")
    database: str = Field(default="blackveil", alias="BV_POSTGRES_DB")
    pool_size: int = Field(default=10, alias="BV_POSTGRES_POOL_SIZE")
    max_overflow: int = Field(default=20, alias="BV_POSTGRES_MAX_OVERFLOW")
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False

    @property
    def connection_string(self) -> str:
        return (
            f"postgresql+asyncpg://{self.username}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class RedisConfig(BaseModel):
    """Redis cache configuration"""
    host: str = Field(default="localhost", alias="BV_REDIS_HOST")
    port: int = Field(default=6379, alias="BV_REDIS_PORT")
    password: Optional[SecretStr] = Field(default=None, alias="BV_REDIS_PASSWORD")
    db: int = Field(default=0, alias="BV_REDIS_DB")
    max_connections: int = 50
    socket_timeout: int = 5
    decode_responses: bool = True

    @property
    def connection_string(self) -> str:
        pw = self.password.get_secret_value() if self.password else ""
        auth = f":{pw}@" if pw else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class MongoDBConfig(BaseModel):
    """MongoDB configuration for document storage"""
    host: str = Field(default="localhost", alias="BV_MONGO_HOST")
    port: int = Field(default=27017, alias="BV_MONGO_PORT")
    username: Optional[str] = Field(default=None, alias="BV_MONGO_USER")
    password: Optional[SecretStr] = Field(default=None, alias="BV_MONGO_PASSWORD")
    database: str = Field(default="blackveil_logs", alias="BV_MONGO_DB")
    max_pool_size: int = 100

    @property
    def connection_string(self) -> str:
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password.get_secret_value()}@"
        return f"mongodb://{auth}{self.host}:{self.port}/{self.database}"


class Neo4jConfig(BaseModel):
    """Neo4j graph database configuration"""
    host: str = Field(default="localhost", alias="BV_NEO4J_HOST")
    port: int = Field(default=7687, alias="BV_NEO4J_PORT")
    username: str = Field(default="neo4j", alias="BV_NEO4J_USER")
    password: SecretStr = Field(default="neo4j", alias="BV_NEO4J_PASSWORD")
    database: str = "neo4j"
    max_connection_pool_size: int = 50


class MinIOConfig(BaseModel):
    """MinIO object storage configuration"""
    host: str = Field(default="localhost", alias="BV_MINIO_HOST")
    port: int = Field(default=9000, alias="BV_MINIO_PORT")
    access_key: str = Field(default="minioadmin", alias="BV_MINIO_ACCESS_KEY")
    secret_key: SecretStr = Field(default="minioadmin", alias="BV_MINIO_SECRET_KEY")
    bucket: str = Field(default="blackveil", alias="BV_MINIO_BUCKET")
    secure: bool = False


# ── Research Engine Configurations ─────────────────────────────

class TTRMConfig(BaseModel):
    """Temporal Trust Recovery Model configuration"""
    healing_rate: float = 0.02
    confidence_recovery_rate: float = 0.01
    max_recovery_time: int = 86400  # 24 hours
    evidence_weight: float = 0.3
    time_decay_constant: int = 3600  # 1 hour
    drift_threshold: float = 3.0
    cusum_allowance: float = 0.5


class ACDMConfig(BaseModel):
    """Adaptive Cyber Deception Model configuration"""
    honeypot_count: int = 10
    twin_count: int = 5
    deception_duration: int = 3600  # 1 hour
    learning_rate: float = 0.1
    realism_threshold: float = 0.8
    max_interactions: int = 1000
    evolution_generations: int = 100
    mutation_rate: float = 0.1


class DCMMConfig(BaseModel):
    """Dynamic Credential Mutation Model configuration"""
    mutation_interval: int = 1800  # 30 minutes
    credential_lifetime: int = 86400  # 24 hours
    complexity_min: int = 16
    genome_size: int = 128
    mutation_rate: float = 0.01
    population_size: int = 50
    fitness_threshold: float = 0.7


class CCEConfig(BaseModel):
    """Cognitive Consensus Engine configuration"""
    confidence_threshold: float = 0.7
    agreement_threshold: float = 0.67
    max_iterations: int = 10
    conflict_resolution_strategy: str = "trust_weighted_voting"
    min_models_required: int = 2
    byzantine_fault_tolerance: int = 1


class LAMGConfig(BaseModel):
    """Living Attack Memory Graph configuration"""
    node_limit: int = 100000
    edge_limit: int = 500000
    similarity_threshold: float = 0.8
    evolution_window: int = 30  # days
    dna_dimension: int = 256
    memory_decay_rate: float = 0.01


class SEEConfig(BaseModel):
    """Security Evolution Engine configuration"""
    learning_interval: int = 3600  # 1 hour
    adaptation_threshold: float = 0.05
    forgetting_rate: float = 0.01
    reorganization_interval: int = 86400  # 24 hours
    max_iterations: int = 1000
    min_accuracy_threshold: float = 0.85


class ATCNConfig(BaseModel):
    """Adaptive Trust Cognitive Network configuration"""
    trust_decay_rate: float = 0.01
    trust_memory_size: int = 10000
    context_dimensions: List[str] = ["role", "environment", "time", "behavior"]
    evidence_window: int = 3600
    learning_rate: float = 0.1
    recovery_rate: float = 0.05


# ── AI Configuration ──────────────────────────────────────────

class AIConfig(BaseModel):
    """AI model configuration"""
    models_path: str = Field(default="models", alias="BV_MODELS_DIR")
    datasets_path: str = Field(default="master_dataset", alias="BV_DATASETS_DIR")
    cache_size: int = 1000
    cache_ttl: int = 300
    ensemble_weights: Dict[str, float] = {
        "cnn": 0.35,
        "dnn": 0.30,
        "xgboost": 0.35,
    }
    confidence_threshold: float = 0.7
    max_parallel_models: int = 4
    use_gpu: bool = True
    batch_size: int = 32
    max_sequence_length: int = 512
    prediction_timeout: int = 30


# ── Security Configuration ────────────────────────────────────

class JWTConfig(BaseModel):
    """JWT authentication configuration"""
    secret_key: SecretStr = Field(default="change-me-in-production", alias="BV_JWT_SECRET")
    algorithm: str = Field(default="HS256", alias="BV_JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="BV_JWT_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="BV_JWT_REFRESH_DAYS")


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO", alias="BV_LOG_LEVEL")
    format: str = Field(default="json", alias="BV_LOG_FORMAT")
    handlers: List[str] = Field(default=["console", "file"], alias="BV_LOG_HANDLERS")
    file_path: str = Field(default="logs", alias="BV_LOG_PATH")
    file_max_bytes: int = Field(default=104857600, alias="BV_LOG_MAX_BYTES")
    file_backup_count: int = Field(default=10, alias="BV_LOG_BACKUP_COUNT")


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration"""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    grafana_url: str = "http://grafana:3000"
    jaeger_enabled: bool = True
    jaeger_agent_host: str = "jaeger-agent"
    jaeger_agent_port: int = 6831


class KafkaConfig(BaseModel):
    """Kafka event streaming configuration"""
    bootstrap_servers: List[str] = Field(
        default=["localhost:9092"], alias="BV_KAFKA_BOOTSTRAP_SERVERS"
    )
    group_id: str = Field(default="blackveil", alias="BV_KAFKA_GROUP_ID")
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False
    max_poll_records: int = 500
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[SecretStr] = None


# ── Main Settings ─────────────────────────────────────────────

class Settings(BaseSettings):
    """Main application settings — all configurable via env vars and YAML"""

    # Application
    app_name: str = "BLACK VEIL V5"
    app_version: str = "5.0.0"
    environment: str = Field(default="development", alias="BV_ENV")
    debug: bool = Field(default=False, alias="BV_DEBUG")

    # Server
    host: str = Field(default="0.0.0.0", alias="BV_HOST")
    port: int = Field(default=8000, alias="BV_PORT")
    workers: int = Field(default=4, alias="BV_WORKERS")
    reload: bool = Field(default=False, alias="BV_RELOAD")

    # Security
    jwt: JWTConfig = JWTConfig()
    api_key_header: str = "X-API-Key"
    cors_origins: List[str] = ["*"]
    allowed_hosts: List[str] = ["*"]
    encryption_key: Optional[str] = Field(default=None, alias="BV_ENCRYPTION_KEY")

    # Databases
    postgres: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()
    mongodb: MongoDBConfig = MongoDBConfig()
    neo4j: Neo4jConfig = Neo4jConfig()
    minio: MinIOConfig = MinIOConfig()

    # Message Queue
    kafka: KafkaConfig = KafkaConfig()

    # AI
    ai: AIConfig = AIConfig()

    # Research Engines
    atcn: ATCNConfig = ATCNConfig()
    ttrm: TTRMConfig = TTRMConfig()
    acdm: ACDMConfig = ACDMConfig()
    dcmm: DCMMConfig = DCMMConfig()
    cce: CCEConfig = CCEConfig()
    lamg: LAMGConfig = LAMGConfig()
    see: SEEConfig = SEEConfig()

    # Logging & Monitoring
    logging: LoggingConfig = LoggingConfig()
    monitoring: MonitoringConfig = MonitoringConfig()

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @classmethod
    def from_yaml(cls, config_path: str) -> "Settings":
        """Load settings from YAML file with env var expansion"""
        path = Path(config_path)
        if not path.exists():
            return cls()

        with open(path) as f:
            raw = yaml.safe_load(f)

        config = cls._expand_env_vars(raw)
        return cls(**config)

    @staticmethod
    def _expand_env_vars(value: Any) -> Any:
        """Recursively expand ${ENV_VAR} patterns in config values"""
        if isinstance(value, dict):
            return {k: Settings._expand_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [Settings._expand_env_vars(v) for v in value]
        elif isinstance(value, str) and "${" in value:
            import re
            def replace_var(match):
                var_name = match.group(1)
                default = None
                if ":-" in var_name:
                    var_name, default = var_name.split(":-", 1)
                return os.environ.get(var_name, default or "")
            return re.sub(r"\$\{([^}]+)\}", replace_var, value)
        return value


def load_settings() -> Settings:
    """Load settings with priority: env vars > YAML config > defaults"""
    env = os.environ.get("BV_ENV", "development")

    # Start with defaults
    settings = Settings()

    # Override with environment-specific YAML if exists
    for config_file in [
        f"config/{env}.yaml",
        "config/local.yaml",
        "config/default.yaml",
    ]:
        path = Path(config_file)
        if path.exists():
            try:
                yaml_settings = Settings.from_yaml(str(path))
                settings = _deep_merge(settings, yaml_settings)
            except Exception:
                pass  # YAML may not contain all fields

    return settings


def _deep_merge(base: Any, override: Any) -> Any:
    """Deep merge two settings objects"""
    if not isinstance(base, type(override)):
        return override

    if isinstance(base, BaseModel):
        # For Pydantic models, iterate fields and merge recursively
        merged = base.model_copy(deep=True)
        for field_name in base.model_fields:
            base_val = getattr(base, field_name)
            override_val = getattr(override, field_name)
            if isinstance(base_val, BaseModel):
                setattr(merged, field_name, _deep_merge(base_val, override_val))
            else:
                setattr(merged, field_name, override_val)
        return merged
    elif isinstance(base, dict):
        merged = base.copy()
        for k, v in override.items():
            if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = _deep_merge(merged[k], v)
            else:
                merged[k] = v
        return merged
    return override


# Global singleton
settings: Settings = load_settings()


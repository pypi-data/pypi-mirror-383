from enum import Enum, StrEnum
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .loop import LoopEvent

E = TypeVar("E", bound="LoopEvent")


class LoopStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    IDLE = "idle"
    STOPPED = "stopped"


class LoopEventSender(StrEnum):
    CLIENT = "client"
    SERVER = "server"


class RedisConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 6379
    database: int = 0
    password: str = ""
    ssl: bool = False


class S3Config(BaseModel):
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    region_name: str = "us-east-1"
    bucket_name: str = "fastloop"
    prefix: str = "fastloop"
    endpoint_url: str = ""


class StateType(str, Enum):
    REDIS = "redis"
    S3 = "s3"


class StateConfig(BaseModel):
    type: str = StateType.REDIS.value
    redis: RedisConfig = RedisConfig()
    s3: S3Config = S3Config()


class CorsConfig(BaseModel):
    enabled: bool = True
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]


class SlackConfig(BaseModel):
    app_id: str
    bot_token: str
    signing_secret: str
    client_id: str


class SurgeConfig(BaseModel):
    token: str
    account_id: str
    base_url: str = "https://api.surge.app"


class IntegrationType(StrEnum):
    SLACK = "slack"
    SURGE = "surge"


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    debug_mode: bool = False
    log_level: str = "INFO"
    pretty_print_logs: bool = True
    loop_delay_s: float = 0.1
    sse_poll_interval_s: float = 0.1
    sse_keep_alive_s: float = 10.0
    shutdown_idle: bool = True
    max_idle_cycles: int = 10
    shutdown_timeout_s: float = 10.0
    port: int = 8000
    host: str = "localhost"
    cors: CorsConfig = CorsConfig()
    state: StateConfig = StateConfig()

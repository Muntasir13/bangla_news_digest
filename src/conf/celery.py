from dataclasses import dataclass


@dataclass
class CeleryBrokerConfig:
    url: str
    heartbeat: int
    connection_max_retries: int


@dataclass
class CeleryResultBackendConfig:
    url: str
    socket_timeout: int


@dataclass
class CeleryTaskConfig:
    max_time_limit: int  # hard kill after 10 minutes
    soft_time_limit: int  # soft warning at 9 minutes
    acks_late: bool
    reject_on_worker_lost: bool
    default_queue: str


@dataclass
class CeleryWorkerConfig:
    pool: str
    concurrency: int
    max_tasks_per_child: int  # recycle processes to avoid leaks
    prefetch_multiplier: int
    hijack_root_logger: bool
    redirect_stdouts: bool


@dataclass
class CeleryConfig:
    broker: CeleryBrokerConfig
    result_backend: CeleryResultBackendConfig
    task_config: CeleryTaskConfig
    worker: CeleryWorkerConfig
    task_serializer: str
    result_serializer: str
    accept_content: list[str]
    enable_utc: bool


# TODO: May add prometheus for monitoring celery tasks

import logging
from datetime import datetime
from typing import Any, cast

import hydra
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from celery.worker.worker import WorkController
from dotenv import load_dotenv
from omegaconf import DictConfig, OmegaConf

from src.conf import CeleryConfig
from src.utils import configure_child_logging, init_logging, log_queue


def get_config(location: str, config_name: str) -> DictConfig:
    with hydra.initialize(version_base=None, config_path=location):
        return hydra.compose(config_name=config_name)


def generate_celery_app() -> Celery:
    cfg = cast(CeleryConfig, get_config(location="../config/celery", config_name="celery"))

    app = Celery("bangla_news_digest")
    app.conf.update(
        broker=cfg.broker.url,
        broker_connection_max_retires=cfg.broker.connection_max_retries,
        broker_heartbeat=cfg.broker.heartbeat,
        result_backend=cfg.result_backend.url,
        redis_socket_timeout=cfg.result_backend.socket_timeout,
        task_serializer=cfg.task_serializer,
        accept_content=cast(list[str], OmegaConf.to_container(cfg.accept_content)),
        result_serializer=cfg.result_serializer,
        task_time_limit=cfg.task_config.max_time_limit,
        task_soft_time_limit=cfg.task_config.soft_time_limit,
        task_acks_late=cfg.task_config.acks_late,
        task_default_queue=cfg.task_config.default_queue,
        worker_prefetch_multiplier=cfg.worker.prefetch_multiplier,
        worker_max_tasks_per_child=cfg.worker.max_tasks_per_child,
        enable_utc=cfg.enable_utc,
        worker_pool=cfg.worker.pool,
        worker_concurrency=cfg.worker.concurrency,
        worker_hijack_root_logger=cfg.worker.hijack_root_logger,
        worker_redirect_stdouts=cfg.worker.redirect_stdouts,
    )
    app.autodiscover_tasks(["runner"])

    return app


@after_setup_logger.connect
def _setup_root(logger: logging.Logger, *args: Any, **kwargs: Any) -> None:
    init_logging(root_logger=logger)


@after_setup_task_logger.connect
def _setup_task(logger: logging.Logger, *args: Any, **kwargs: Any) -> None:
    configure_child_logging(root_logger=logger, log_queue=log_queue)


if __name__ == "__main__":
    load_dotenv()
    app = generate_celery_app()
    app.control.purge()
    celery_worker = WorkController(app=app, hostname=f"worker_{datetime.now()}", loglevel="INFO")  # type: ignore
    celery_worker.start()  # type: ignore

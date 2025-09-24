import logging
import os
import sys
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from multiprocessing import Queue

from pythonjsonlogger.json import JsonFormatter

from src.conf import LoggerConfig


def init_logging(cfg: LoggerConfig) -> tuple[logging.Logger, Queue[dict[str, str]], QueueListener]:
    # Creating Save Location if not present
    if not os.path.exists(cfg.file.folder_location):
        os.makedirs(cfg.file.folder_location)

    # STDOUT handler with JSON formatting
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_fmt = JsonFormatter(fmt=cfg.fmt)
    stdout_handler.setFormatter(stdout_fmt)

    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(cfg.file.folder_location, cfg.file.name),
        when="midnight",
        backupCount=7,  # keep one week of logs
        utc=True,
    )
    file_fmt = JsonFormatter(fmt=cfg.fmt)
    file_handler.setFormatter(file_fmt)

    # Multiprocessing queue for log records
    log_queue: Queue[dict[str, str]] = Queue(-1)  # infinite queue size

    # QueueListener for the main process
    listener = QueueListener(log_queue, stdout_handler, file_handler, respect_handler_level=True)
    listener.start()

    # Base Logger
    qh = QueueHandler(log_queue)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []  # ensures listener is the one writing logs
    root_logger.addHandler(qh)

    return root_logger, log_queue, listener


def configure_child_logging(log_queue: Queue[dict[str, str]]) -> None:
    qh = QueueHandler(log_queue)
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(qh)
    root_logger.setLevel(logging.INFO)

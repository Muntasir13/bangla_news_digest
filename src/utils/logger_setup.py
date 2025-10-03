import logging
import os
import sys
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from multiprocessing import Queue

from pythonjsonlogger.json import JsonFormatter

# Multiprocessing queue for log records
log_queue: Queue = Queue(-1)  # infinite queue size


def init_logging(root_logger: logging.Logger) -> None:
    """This method updates the logger configuration already produced by Hydra
    with the custom logger configuration with a QueueListener to add multiprocessing logging

    Returns:
        tuple[logging.Logger, Queue, QueueListener]: logger, log_queue and the queue listener
    """
    # Logger String Format
    fmt = "%(asctime)s %(processName)s %(name)s %(levelname)s %(message)s"

    # STDOUT handler with JSON formatting
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_fmt = JsonFormatter(fmt=fmt)
    stdout_handler.setFormatter(stdout_fmt)

    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join("celery_app.log"),
        when="midnight",
        backupCount=7,  # keep one week of logs
        utc=True,
    )
    file_fmt = JsonFormatter(fmt=fmt)
    file_handler.setFormatter(file_fmt)

    # QueueListener for the main process
    listener = QueueListener(log_queue, stdout_handler, file_handler, respect_handler_level=True)
    listener.start()

    # Base Logger
    qh = QueueHandler(log_queue)
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []  # ensures listener is the one writing logs
    root_logger.addHandler(qh)


def configure_child_logging(root_logger: logging.Logger, log_queue: Queue) -> None:
    qh = QueueHandler(log_queue)
    root_logger.handlers = []
    root_logger.addHandler(qh)
    root_logger.setLevel(logging.INFO)

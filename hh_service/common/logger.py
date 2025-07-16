import logging
import sys

import structlog
from structlog.processors import TimeStamper
from structlog.stdlib import ProcessorFormatter, add_log_level, add_logger_name


def setup_logging():
    timestamper = TimeStamper(fmt="iso", utc=True)
    pre_chain = [add_logger_name, add_log_level, timestamper]

    structlog.configure(
        processors=pre_chain + [ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = ProcessorFormatter(
        foreign_pre_chain=pre_chain,
        processors=[
            ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel("DEBUG")

    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True


setup_logging()
logger = structlog.get_logger()

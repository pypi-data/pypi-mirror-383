import structlog

from . import config

processors = [
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
    structlog.processors.dev.set_exc_info,
    structlog.contextvars.merge_contextvars,
]

LOG_LEVEL = config.config.LOG_LEVEL

structlog.configure(
    processors=processors,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

logger.info("Logger initialized")

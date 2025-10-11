from typing import Optional
import logging
import logging.config
import structlog
from structlog import contextvars
from structlog.typing import EventDict
from seismos_package.logging.configuration import get_default_logging_conf
from structlog.dev import ConsoleRenderer


class LoggingConfigurator:
    def __init__(
        self,
        service_name: str,
        log_level: str = "INFO",
        config: Optional[dict] = None,
        setup_logging_dict: bool = False,
    ):
        self.service_name = service_name
        self.log_level = log_level.upper()
        self.config = config
        self.setup_logging_dict = setup_logging_dict

    @staticmethod
    def add_logger_name(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
        """
        Adds the logger name to the log event dictionary, keeping compatibility with structlog's
        processor signature. The `method_name` parameter is included to maintain compatibility with structlog's
        processor signature but is not used directly in this method.
        """

        record = event_dict.get("_record")
        event_dict["name"] = record.name if record else logger.name
        return event_dict

    def get_base_processors(self) -> list:
        """Returns the base processors for structlog, common to all formats."""
        return [
            contextvars.merge_contextvars,
            self.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.stdlib.ExtraAdder(),
            structlog.processors.EventRenamer(to="message"),
        ]

    def get_processors(self, formatter: str = "json_formatter") -> list:
        """
        Returns processors based on the formatter type.
        """
        processors = self.get_base_processors()

        if formatter == "plain_console":
            processors.append(ConsoleRenderer(colors=True))
        else:
            processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)

        return processors

    def configure_structlog(
        self,
        custom_processors: Optional[list] = None,
        formatter: str = "json_formatter",
        formatter_std_lib: str = "json_formatter",
    ) -> None:
        """Configures the structlog and standard Python logging."""
        if self.setup_logging_dict:
            logger_init_config = self.config or get_default_logging_conf(
                log_level=self.log_level,
                formatter=formatter,
                formatter_std_lib=formatter_std_lib,
            )

            logging.config.dictConfig(logger_init_config)

        processors = custom_processors or self.get_processors(formatter=formatter)

        structlog.configure(
            processors=processors,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

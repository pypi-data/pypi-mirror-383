import argparse
import contextlib
import datetime
import logging
import os
from collections.abc import Iterable
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

__all__ = [
    "LoggerHandler",
]

FILE_HANDLER_LOGGER_LEVEL = "FILE_HANDLER_LOGGER_LEVEL"
STREAM_HANDLER_LOGGER_LEVEL = "STREAM_HANDLER_LOGGER_LEVEL"


def get_handler_logger_level_factory(handler_env_var_name: str = ""):
    """
    Factory to create utility functions to retrieve a handler logger level

    :param handler_env_var_name: the name of the env variable that stores the
    handler logger level
    :return: the created function
    """

    def get_handler_logger_level() -> str | int:
        """
        Utility function that returns the handler level retireved from cli
        arguments or from env variable.
        If the script is executed from the cli, overwrite possible handler level
        value retrieved from env variable.

        If not specified, set the level to logging.INFO

        :return: the handler level
        """
        handler_level: str | int = ""

        if level := os.environ.get(handler_env_var_name):
            handler_level = level

        if __name__ == "__main__" and (
            level := getattr(
                cli_parser.parse_args(), handler_env_var_name.lower(), None
            )
        ):
            handler_level = level

        # The level can be a str or an int but env variable are always read as
        # string (argparse can accept a single type used to convert the input),
        # thus we try to convert the handler_level value to int in case the
        # value is set as int
        with contextlib.suppress(ValueError, TypeError):
            handler_level = int(handler_level)

        # Check that the level is a valid level, else set it to "INFO" (20)
        try:
            logging._checkLevel(handler_level)  # type: ignore
        except (ValueError, TypeError):
            handler_level = logging.INFO

        return handler_level

    get_handler_logger_level.__name__ = f"get_{handler_env_var_name.lower()}"

    return get_handler_logger_level


get_file_handler_logger_level = get_handler_logger_level_factory(
    FILE_HANDLER_LOGGER_LEVEL
)
get_stream_handler_logger_level = get_handler_logger_level_factory(
    STREAM_HANDLER_LOGGER_LEVEL
)


class AbstractFormatter(logging.Formatter):
    """
    Abstract Formatter for log messages
    """

    msg_format = " - ".join(
        [
            "%(name)s",
            "%(asctime)s",
            "%(levelname)s",
            "%(message)s",
        ]
    )

    level_formats_keys = (
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    )
    level_formats_values: Iterable[str] = tuple()

    def set_formats(self):
        """
        Method that needs to be implemented in concrete child classes.

        It needs to overwrite the self.level_formats_values with an interable
        of log formatted strings.
        """
        raise NotImplementedError("set_formats method needs to be implemented")

    def get_formats(self) -> dict:
        """
        Method that executes the self.set_formats if
        self.leve_formats_values == None

        :return: the formats dict
        k == log_level
        v == log_level formatting
        """
        if not self.level_formats_values:
            self.set_formats()

        return {
            k: v
            for k, v in zip(
                self.level_formats_keys, self.level_formats_values, strict=True
            )
        }

    def format(self, record):
        """
        Function that sets format linked to the level of the record
        """
        log_fmt = self.get_formats().get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class FileFormatter(AbstractFormatter):
    """
    File Formatter
    """

    def set_formats(self) -> None:
        """
        Method that set the self.level_formats_values
        """
        self.level_formats_values = (f"{self.msg_format}",) * len(
            self.level_formats_keys
        )


class StreamFormatter(AbstractFormatter):
    """
    Stream Formatter
    """

    CYAN = "\x1b[36;20m"
    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED_BG = "\x1b[41;1m"

    colors = (
        CYAN,
        GREY,
        YELLOW,
        RED,
        BOLD_RED_BG,
    )

    RESET = "\x1b[0m"

    def set_formats(self) -> None:
        """
        Method that set the self.level_formats_values
        """
        self.level_formats_values = tuple(
            f"{color}{self.msg_format}{self.RESET}" for color in self.colors
        )


class LoggerHandler:
    """
    Utility class that allows the user to customize the logger name with a
    single <path/filename> log file.

    Basic usage:
    - Create a logger.py file and initialize the LoggerHandler class:

      logger_handler = LoggerHandler()

    - Import the logger_handler in each file that will log messages and assign
      the result of logger_handler.get_logger(__name__) to the logger variable:

      from logger import logger_handler

      logger = logger_handler.get_logger(__name__)

    - Log messages with the logging.Logger methods:
      - logger.debug(<msg>)
      - logger.info(<msg>)
      - logger.warning(<msg>)
      - logger.error(<msg>)
      - logger.critical(<msg>)
    """

    def __init__(
        self,
        filename: str = "app.log",
        path: str = "logs",
        extra_handlers: list[logging.Handler] | None = None,
    ) -> None:
        """
        Class initialization

        :param filename: the log filename
        :param path: the log file's path
        :param extra_handlers: list of additional logging.Handler instances
        to attach to every logger created by get_logger().
        """
        self.filename = filename
        self.extra_handlers = extra_handlers or []
        try:
            self.path = Path(path)
        except TypeError:
            self.path = Path("logs")
        finally:
            if not self.path.exists():
                Path.mkdir(self.path)

    def get_logger(
        self,
        logger_name: str = __name__,
        rotation_interval: str = "W6",  # run every sunday
        rotation_time: datetime.time = datetime.time(23),  # at 23:00
        rotation_backup: int = 10,  # rotate after 10 weeks
    ) -> logging.Logger:
        """
        Function that initializes the logger, set the log rotation,
        configures the file_handler, the stream_handler and additional handlers.

        :param logger_name: the logger name
        :param rotation_interval: the time rotating file handler's "when" param
        :param rotation_time: the time rotating file handler's "atTime" param
        :param rotation_backup: the time rotating file handler's "backupCount" param
        :return: a logging.Logger instance
        """
        logger = logging.getLogger(logger_name)
        # set the "lowest" logging level to the logger instance, otherwise
        # handlers' level will be WARNING (the default level assigned
        # to root logger)
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            file_handler = TimedRotatingFileHandler(
                filename=Path.joinpath(self.path, self.filename),
                when=rotation_interval,
                atTime=rotation_time,
                backupCount=rotation_backup,
            )
            file_handler.setFormatter(FileFormatter())
            file_handler.setLevel(get_file_handler_logger_level())

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(StreamFormatter())
            stream_handler.setLevel(get_stream_handler_logger_level())

            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)

            for extra_handler in self.extra_handlers:
                if not any(isinstance(h, type(extra_handler)) for h in logger.handlers):
                    logger.addHandler(extra_handler)

        return logger


if __name__ == "__main__":
    # logger handler level cli parse and arguments
    default_level_name = logging._levelToName.get(logging.INFO)

    cli_parser = argparse.ArgumentParser()

    cli_parser.add_argument(
        "-fl",
        f"--{FILE_HANDLER_LOGGER_LEVEL.lower().replace('_', '-')}",
        help="Set the file logger level",
    )
    cli_parser.add_argument(
        "-sl",
        f"--{STREAM_HANDLER_LOGGER_LEVEL.lower().replace('_', '-')}",
        help="Set the stream logger level",
    )

    # try logger
    logger_handler = LoggerHandler()
    logger = logger_handler.get_logger(
        rotation_interval="W0",
        rotation_time=datetime.time(0),
        rotation_backup=1,
    )

    for handler in logger.handlers:
        print(f"{type(handler)} level: {handler.level}")

        if isinstance(handler, TimedRotatingFileHandler):
            print(f'File handler "when" param: {handler.when}')
            print(f'File handler "atTime" param: {handler.atTime}')
            print(f'File handler "backupCount" param: {handler.backupCount}')

    logger.debug("Hi from the logger package")
    logger.info("Hi from the logger package")
    logger.warning("Hi from the logger package")
    logger.error("Hi from the logger package")
    logger.critical("Hi from the logger package")

from typing import Any

import structlog

from ganicas_utils.config import Config


def get_default_logging_conf(log_level: str, formatter: str, formatter_std_lib: str) -> dict[str, Any]:
    config_instance = Config()
    app_name = config_instance.APP_NAME

    formatters = {
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "json_formatter": {
            "()": "ganicas_utils.logging.formatter.LogFormatter",
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(event_key="message"),
        },
        "plain_console_std_lib": {
            "()": "logging.Formatter",
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(
                key_order=["microservice", "timestamp", "level", "event", "logger"]
            ),
        },
    }

    if formatter not in formatters or formatter_std_lib not in formatters:
        raise NotImplementedError("formatter not supported")

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": formatter,
            },
            "console_std_lib": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": formatter_std_lib,
            },
        },
        "loggers": {
            "": {
                "level": log_level,
                "handlers": ["console_std_lib"],
                "propagate": False,
            },
        },
    }

    config["loggers"][app_name] = {
        "level": log_level,
        "handlers": ["console"],
        "propagate": False,
    }

    return config

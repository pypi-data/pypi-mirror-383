from datetime import datetime, timezone

from pythonjsonlogger import jsonlogger

from ganicas_utils.config import config


class LogFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["microservice"] = config.APP_NAME
        if not log_record.get("timestamp"):
            now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        log_record["level"] = log_record.get("level", record.levelname).upper()

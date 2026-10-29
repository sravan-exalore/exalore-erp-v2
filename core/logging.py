import json
import logging
from datetime import datetime, timezone
from core.database.context import get_current_database


class TenantContextFilter(logging.Filter):
    """
    Injects the active tenant database alias into all log records automatically.
    """

    def filter(self, record):
        tenant = get_current_database()
        record.tenant = tenant if tenant else "default"
        return True


class JsonFormatter(logging.Formatter):
    """
    Formats log records into machine-readable JSON for centralized log aggregators
    (e.g., Datadog, AWS CloudWatch, ELK stack).
    """

    def format(self, record):
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "tenant": getattr(record, "tenant", "default"),
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "request_id"):
            log_payload["request_id"] = record.request_id

        return json.dumps(log_payload)


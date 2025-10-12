import logging
import logging.handlers
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

# Module-level definitions
APP_ENV = 'prod' # os.getenv("APP_ENV", "dev").lower()
DEFAULT_DISPLAY_ON_STDOUT = (APP_ENV != "prod")  # True for dev, False for prod


# ---------------- custom Logger that accepts display_on_stdout --------------
class AppLogger(logging.Logger):
    """Logger that accepts a per-call 'display_on_stdout' kwarg (env-based default)."""

    def _with_stdout_flag(self, kwargs, display_on_stdout: bool):
        # Merge the flag into record.extra without mutating caller's dict
        extra = dict(kwargs.get("extra") or {})
        extra["display_on_stdout"] = display_on_stdout
        kwargs["extra"] = extra
        return kwargs

    # Use env-based default in all logging methods
    def debug(self, msg, *args, display_on_stdout: bool = DEFAULT_DISPLAY_ON_STDOUT, **kwargs):
        kwargs = self._with_stdout_flag(kwargs, display_on_stdout)
        super().debug(msg, *args, **kwargs)

    def info(self, msg, *args, display_on_stdout: bool = DEFAULT_DISPLAY_ON_STDOUT, **kwargs):
        kwargs = self._with_stdout_flag(kwargs, display_on_stdout)
        super().info(msg, *args, **kwargs)

    def warning(self, msg, *args, display_on_stdout: bool = True, **kwargs):
        kwargs = self._with_stdout_flag(kwargs, display_on_stdout)
        super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, display_on_stdout: bool = True, **kwargs):
        kwargs = self._with_stdout_flag(kwargs, display_on_stdout)
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, display_on_stdout: bool = DEFAULT_DISPLAY_ON_STDOUT, **kwargs):
        kwargs = self._with_stdout_flag(kwargs, display_on_stdout)
        super().critical(msg, *args, **kwargs)

    def exception(self, msg, *args, display_on_stdout: bool = DEFAULT_DISPLAY_ON_STDOUT, **kwargs):
        kwargs.setdefault("exc_info", True)
        kwargs = self._with_stdout_flag(kwargs, display_on_stdout)
        super().error(msg, *args, **kwargs)


logging.setLoggerClass(AppLogger)

# --------------- filter that hides records from stdout if needed ------------
class StdoutDisplayFilter(logging.Filter):
    """Allow a record to reach the console only if display_on_stdout flag permits."""
    def filter(self, record: logging.LogRecord) -> bool:
        # Use env-based default if the record doesn't specify the flag
        return getattr(record, "display_on_stdout", DEFAULT_DISPLAY_ON_STDOUT)


class ServiceLogger:
    """Centralized logging configuration for the service"""

    _instance: Optional['ServiceLogger'] = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logger()
            ServiceLogger._initialized = True

    def _setup_logger(self):
        """Setup comprehensive logging configuration"""

        # Use our custom logger class globally (must be before getLogger calls)

        # Create logs directory if it doesn't exist
        self.logs_dir = "logs"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        root_logger.handlers.clear()

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Setup file handlers
        self._setup_file_handlers(detailed_formatter)

        # Setup console handler (honors per-record display_on_stdout)
        self._setup_console_handler(simple_formatter)

        # Log initialization
        logging.info(f"===  Service Logger Initialized ===")
        logging.info(f"Log files location: {os.path.abspath(self.logs_dir)}")

    def _setup_file_handlers(self, formatter):
        """Setup rotating file handlers for different log levels"""

        # Main application log (INFO and above)
        main_log_file = os.path.join(self.logs_dir, "service.log")
        main_handler = logging.handlers.RotatingFileHandler(
            main_log_file, maxBytes=10*1024*1024, backupCount=5
        )
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(formatter)
        logging.getLogger().addHandler(main_handler)

        # Error log (ERROR and above)
        error_log_file = os.path.join(self.logs_dir, "errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=5*1024*1024, backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logging.getLogger().addHandler(error_handler)

        # Debug log (DEBUG and above) - only in development
        if os.getenv('DEBUG', 'False').lower() == 'true':
            debug_log_file = os.path.join(self.logs_dir, "debug.log")
            debug_handler = logging.handlers.RotatingFileHandler(
                debug_log_file, maxBytes=20*1024*1024, backupCount=2
            )
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(formatter)
            logging.getLogger().addHandler(debug_handler)

    # def _setup_console_handler(self, formatter):
    #     """Setup console handler with appropriate level and per-record suppression"""
    #     console_handler = logging.StreamHandler(sys.stdout)

    #     # Set console level based on environment
    #     console_level = os.getenv('CONSOLE_LOG_LEVEL', 'INFO').upper()
    #     console_handler.setLevel(getattr(logging, console_level, logging.INFO))
    #     console_handler.setFormatter(formatter)

    #     # Add filter to hide records when display_on_stdout=False
    #     console_handler.addFilter(StdoutDisplayFilter())

    #     logging.getLogger().addHandler(console_handler)

    # def _setup_console_handler(self, formatter):
    #     """Setup console handler with all levels allowed; per-record suppression via filter."""
    #     console_handler = logging.StreamHandler(sys.stdout)

    #     # Allow ALL levels to pass the handler (DEBUG through CRITICAL)
    #     console_handler.setLevel(logging.NOTSET)

    #     console_handler.setFormatter(formatter)
    
    #     # Keep the filter so display_on_stdout controls visibility
    #     console_handler.addFilter(StdoutDisplayFilter())

    #     logging.getLogger().addHandler(console_handler)


    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance for a specific module"""
        ServiceLogger()
        return logging.getLogger(name)


# Convenience function for easy import
def setup_logger(name: str):
    """Initialize the service logger and set global service name"""
    return ServiceLogger()

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module"""
    return ServiceLogger.get_logger(name)

def clear_logs():
    """Delete the logs directory and its contents."""
    import shutil
    logs_dir = "logs"
    if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
        shutil.rmtree(logs_dir)

def clear_logs_before(cutoff: str) -> None:
    """Purge log entries older than 'cutoff' from service.log and errors.log.

    cutoff accepts 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'.
    """
    cutoff_dt = _parse_cutoff(cutoff)
    log_files = [
        os.path.join("logs", "service.log"),
        os.path.join("logs", "errors.log"),
    ]
    for file_path in log_files:
        _truncate_log_file(file_path, cutoff_dt)

def _parse_cutoff(cutoff: str) -> datetime:
    """Parse cutoff string to datetime."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(cutoff, fmt)
            if fmt == "%Y-%m-%d":
                return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
            return dt
        except ValueError:
            continue
    raise ValueError("Invalid cutoff format. Use 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'.")

def _truncate_log_file(file_path: str, cutoff_dt: datetime) -> None:
    """Rewrite log file keeping only entries with timestamp >= cutoff_dt.

    Handles multi-line entries by treating a new record when a line starts
    with the timestamp 'YYYY-MM-DD HH:MM:SS'.
    """
    if not os.path.exists(file_path):
        return
    tmp_path = file_path + ".tmp"
    ts_re = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\\b")

    current_keep = True
    with open(file_path, "r", encoding="utf-8", errors="ignore") as src, \
         open(tmp_path, "w", encoding="utf-8") as dst:
        for line in src:
            m = ts_re.match(line)
            if m:
                try:
                    ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                    current_keep = ts >= cutoff_dt
                except ValueError:
                    current_keep = True
            if current_keep:
                dst.write(line)

    os.replace(tmp_path, file_path)

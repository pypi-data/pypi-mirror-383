"""
Structured Logging for AI Agents

Provides structured logging with levels, context, and formatting
for production debugging and monitoring.

Supports:
- Multiple log levels (DEBUG, INFO, WARN, ERROR, CRITICAL)
- Structured fields (JSON format)
- Context propagation
- Log aggregation (CloudWatch, DataDog, ELK)
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum


class LogLevel(str, Enum):
    """Log levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AgentLogger:
    """
    Structured logger for AI agents

    Features:
    - Structured logging with JSON format
    - Contextual information (agent, execution_id)
    - Multiple outputs (file, stdout, custom handlers)
    - Log rotation
    - Filtering by level

    Example:
        ```python
        logger = AgentLogger(
            agent_name="research-assistant",
            log_file="logs/agent.log",
            level=LogLevel.INFO
        )

        # Simple logging
        logger.info("Agent started")
        logger.debug("Processing query", extra={"query": "..."})

        # With context
        with logger.context(execution_id="exec-123"):
            logger.info("Executing task")
            logger.error("Task failed", error=str(e))
        ```
    """

    def __init__(
        self,
        agent_name: str = "default",
        log_file: Optional[str] = None,
        level: LogLevel = LogLevel.INFO,
        json_format: bool = True,
        include_timestamp: bool = True,
        include_agent: bool = True,
    ):
        """
        Initialize logger

        Args:
            agent_name: Name of the agent
            log_file: Path to log file (None = stdout only)
            level: Minimum log level
            json_format: Use JSON formatting
            include_timestamp: Include timestamp in logs
            include_agent: Include agent name in logs
        """
        self.agent_name = agent_name
        self.json_format = json_format
        self.include_timestamp = include_timestamp
        self.include_agent = include_agent
        self._context: Dict[str, Any] = {}

        # Create logger
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.logger.setLevel(self._get_logging_level(level))
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(file_handler)

    def _get_logging_level(self, level: LogLevel) -> int:
        """Convert LogLevel to logging level"""
        mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARN: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return mapping[level]

    def _get_formatter(self) -> logging.Formatter:
        """Get log formatter"""
        if self.json_format:
            return _JSONFormatter(
                agent_name=self.agent_name,
                include_timestamp=self.include_timestamp,
                include_agent=self.include_agent,
            )
        else:
            return logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

    def _build_record(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Build log record with context"""
        record = {
            "message": message,
            **self._context,  # Include context
            **(extra or {}),  # Include extra fields
            **kwargs,  # Include kwargs
        }

        if self.include_agent:
            record["agent"] = self.agent_name

        if self.include_timestamp:
            record["timestamp"] = datetime.now().isoformat()

        return record

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log debug message

        Args:
            message: Log message
            extra: Extra structured fields
            **kwargs: Additional fields
        """
        record = self._build_record(message, extra, **kwargs)
        self.logger.debug(json.dumps(record) if self.json_format else message, extra=record)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log info message

        Args:
            message: Log message
            extra: Extra structured fields
            **kwargs: Additional fields
        """
        record = self._build_record(message, extra, **kwargs)
        self.logger.info(json.dumps(record) if self.json_format else message, extra=record)

    def warn(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log warning message

        Args:
            message: Log message
            extra: Extra structured fields
            **kwargs: Additional fields
        """
        record = self._build_record(message, extra, **kwargs)
        self.logger.warning(json.dumps(record) if self.json_format else message, extra=record)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log error message

        Args:
            message: Log message
            extra: Extra structured fields
            **kwargs: Additional fields
        """
        record = self._build_record(message, extra, **kwargs)
        self.logger.error(json.dumps(record) if self.json_format else message, extra=record)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log critical message

        Args:
            message: Log message
            extra: Extra structured fields
            **kwargs: Additional fields
        """
        record = self._build_record(message, extra, **kwargs)
        self.logger.critical(json.dumps(record) if self.json_format else message, extra=record)

    def exception(self, message: str, exc_info: bool = True, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log exception with traceback

        Args:
            message: Log message
            exc_info: Include exception info
            extra: Extra structured fields
            **kwargs: Additional fields
        """
        record = self._build_record(message, extra, **kwargs)
        self.logger.exception(
            json.dumps(record) if self.json_format else message,
            exc_info=exc_info,
            extra=record
        )

    def context(self, **kwargs) -> "_LoggerContext":
        """
        Create a logging context

        Args:
            **kwargs: Context fields to add

        Returns:
            Context manager

        Example:
            ```python
            with logger.context(execution_id="123", user="john"):
                logger.info("Processing")  # Includes execution_id and user
            ```
        """
        return _LoggerContext(self, kwargs)


class _JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def __init__(self, agent_name: str, include_timestamp: bool, include_agent: bool):
        super().__init__()
        self.agent_name = agent_name
        self.include_timestamp = include_timestamp
        self.include_agent = include_agent

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if self.include_timestamp:
            log_data["timestamp"] = datetime.fromtimestamp(record.created).isoformat()

        if self.include_agent:
            log_data["agent"] = self.agent_name

        # Include extra fields from record.__dict__
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "pathname", "process", "processName", "relativeCreated",
                          "thread", "threadName", "exc_info", "exc_text", "stack_info"]:
                log_data[key] = value

        return json.dumps(log_data)


class _LoggerContext:
    """Context manager for logging context"""

    def __init__(self, logger: AgentLogger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
        self.previous_context: Dict[str, Any] = {}

    def __enter__(self):
        # Save previous context
        self.previous_context = self.logger._context.copy()
        # Add new context
        self.logger._context.update(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous context
        self.logger._context = self.previous_context
        return False

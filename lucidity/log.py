from builtins import BaseExceptionGroup
import logging
from logging import FileHandler, Handler, StreamHandler
import sys
import traceback
from types import TracebackType
from typing import Any

from rich.logging import RichHandler

logger = logging.getLogger("lucidity")


def setup_logging(
    log_level: str,
    debug: bool,
    handler: Handler | None = None,
    log_file: str | None = None,
    console_enabled: bool = True,
    stderr_only: bool = False,
) -> None:
    """Configure logging for the application.

    Args:
        log_level: The logging level to use
        debug: Whether debug mode is enabled
        handler: The RichHandler to use for logging (created if not provided)
        log_file: Path to log file (if file logging is enabled)
        console_enabled: Whether to enable console logging
        stderr_only: Whether to log only to stderr (for stdio transport without log file)
    """
    handlers = []

    # Add console handler if enabled (normal console mode with rich output)
    if console_enabled and not stderr_only:
        if handler is None:
            handler = RichHandler(rich_tracebacks=True, markup=True)
        handlers.append(handler)

    # Add stderr handler if we're in stderr-only mode
    if stderr_only:
        stderr_handler = StreamHandler(sys.stderr)
        stderr_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        )
        # Only log warnings and above to stderr
        stderr_handler.setLevel(logging.WARNING)
        handlers.append(stderr_handler)

    # Add file handler if log_file is provided
    if log_file:
        file_handler = FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        )
        handlers.append(file_handler)

    # Configure basic logging
    if handlers:
        # Only set up if we have handlers
        logging.basicConfig(
            level=getattr(logging, str(log_level)),
            format="%(message)s",
            datefmt="[%X]",
            handlers=handlers,
            force=True,
        )

        # Configure the main logger
        logger.setLevel(logging.DEBUG if debug else getattr(logging, log_level))
        logger.handlers = handlers
        logger.propagate = False

        # Also configure Uvicorn loggers with our handlers
        for uv_logger in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
            uvicorn_logger = logging.getLogger(uv_logger)
            uvicorn_logger.handlers = handlers
            uvicorn_logger.propagate = False

        # Set higher log level for protocol-level logs
        logging.getLogger("mcp.server.sse").setLevel(logging.INFO)
        logging.getLogger("mcp.server.stdio").setLevel(logging.INFO)
        logging.getLogger("mcp.server.fastmcp").setLevel(logging.INFO)
        logging.getLogger("starlette").setLevel(logging.INFO)
        logging.getLogger("uvicorn").setLevel(logging.INFO)

        # Configure additional loggers if verbose mode
        if debug:
            # Set up more detailed logging for the requests library
            requests_logger = logging.getLogger("urllib3")
            requests_logger.setLevel(logging.DEBUG)
            if not stderr_only:
                logger.debug("Verbose logging enabled for HTTP requests")


# Custom exception handler for TaskGroup exceptions
def handle_taskgroup_exception(exc: BaseException) -> None:
    """Handle TaskGroup exceptions by extracting and logging all nested exceptions.

    Args:
        exc: The exception to handle
    """
    # Log the main exception
    logger.error("TaskGroup exception occurred: %s", exc)

    # Extract and log all nested exceptions
    if isinstance(exc, BaseExceptionGroup):
        for i, e in enumerate(exc.exceptions):
            logger.error("TaskGroup sub-exception %d: %s", i + 1, e)
            logger.error("".join(traceback.format_exception(type(e), e, e.__traceback__)))

    # Check for __context__ attribute (chained exceptions)
    if hasattr(exc, "__context__") and exc.__context__ is not None:
        logger.error("Chained exception: %s", exc.__context__)
        logger.error(
            "".join(traceback.format_exception(type(exc.__context__), exc.__context__, exc.__context__.__traceback__))
        )


def setup_asyncio_exception_handler() -> None:
    """Set up the asyncio exception handler."""
    import asyncio

    # Set up asyncio exception handler
    def asyncio_exception_handler(_loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
        # Extract exception
        exception = context.get("exception")
        if exception:
            logger.error("Unhandled asyncio exception: %s", exception)
            handle_taskgroup_exception(exception)
        else:
            logger.error("Unhandled asyncio error: %s", context["message"])

    # Get the current event loop and set the exception handler
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(asyncio_exception_handler)


def setup_global_exception_handler() -> None:
    """Set up the global exception handler."""

    def global_exception_handler(
        exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            # Let KeyboardInterrupt pass through
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # For all other exceptions, log them with our custom handler
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        # Also handle TaskGroup exceptions
        handle_taskgroup_exception(exc_value)

    # Install the global exception handler
    sys.excepthook = global_exception_handler

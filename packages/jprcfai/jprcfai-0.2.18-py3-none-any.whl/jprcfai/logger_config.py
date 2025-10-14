#!/usr/bin/env python3
import logging
import os
import sys

# Create a module-level logger. You could also use __name__ if you prefer.
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.INFO)


def setup_logger() -> None:
    """
    Set up or reconfigure the logger based on the current environment variables.
    It clears any existing handlers, then adds a FileHandler if
    JPRCFAI_DEBUG_FILE_OUTPUT is set and/or a StreamHandler if JPRCFAI_DEBUG_STDOUT is set.
    If neither is provided, the logger is disabled.
    """
    # Remove any previously attached handlers.
    logger.handlers.clear()

    debug_file = os.getenv("JPRCFAI_DEBUG_FILE_OUTPUT", "").strip()
    debug_stdout = os.getenv("JPRCFAI_DEBUG_STDOUT", "").strip()

    # Add FileHandler if a file path is provided.
    if debug_file:
        try:
            file_handler = logging.FileHandler(debug_file)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            logger.addHandler(file_handler)
            logger.info("Logging to file enabled at: %s", debug_file)
        except Exception as e:
            logger.error("Failed to add FileHandler: %s", e)

    # Add StreamHandler if stdout logging is enabled.
    if debug_stdout:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(stream_handler)
        logger.info("Logging to stdout enabled.")

    # Disable logging if no outputs are provided.
    if not debug_file and not debug_stdout:
        logger.disabled = True
    else:
        logger.disabled = False


# Initial configuration on module load.
setup_logger()


def reevaluate_logger_configuration() -> None:
    """
    Re-evaluate the logger configuration by re-running setup_logger.
    Call this function if you need to adjust logging during runtime.
    """
    setup_logger()

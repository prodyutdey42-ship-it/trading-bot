import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(
    logger_name="trading_bot",
    log_dir="logs",
    log_file="trading_bot.log",
    file_level=logging.DEBUG,
    console_level=logging.INFO,
    max_bytes=10 * 1024 * 1024,  # 10 MB
    backup_count=5,
    log_format="%(asctime)s | %(levelname)s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s",
):
    """
    Sets up and returns a configured logger with file and console handlers.

    Args:
        logger_name: Name of the logger instance.
        log_dir: Directory to store log files.
        log_file: Name of the log file.
        file_level: Logging level for the file handler.
        console_level: Logging level for the console handler.
        max_bytes: Maximum size of a single log file before rotation.
        backup_count: Number of rotated log files to keep.
        log_format: Format string for log messages.

    Returns:
        logging.Logger: Configured logger instance.
    """

    
    logger = logging.getLogger(logger_name)

    
    if getattr(logger, "_is_configured", False):
        return logger

    
    logger.setLevel(min(file_level, console_level))

    
    logger.propagate = False

    
    formatter = logging.Formatter(log_format)

    
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_file)

        
        fh = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",  
        )
        fh.setLevel(file_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    except (OSError, PermissionError) as e:
        
        print(
            f"WARNING: Could not set up file logging at "
            f"'{os.path.join(log_dir, log_file)}': {e}"
        )

    
    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    
    logger._is_configured = True

    return logger


def reset_logger(logger_name="trading_bot"):
    """
    Resets the logger by removing all handlers and clearing the
    configured flag. Useful for testing or reconfiguration.

    Args:
        logger_name: Name of the logger to reset.
    """
    logger = logging.getLogger(logger_name)

    
    for handler in logger.handlers[:]:  
        try:
            handler.close()
        except Exception:
            pass
        logger.removeHandler(handler)

    logger._is_configured = False



if __name__ == "__main__":
    
    logger = setup_logger()
    logger.debug("This is a DEBUG message   (file only)")
    logger.info("This is an INFO message    (file + console)")
    logger.warning("This is a WARNING message  (file + console)")
    logger.error("This is an ERROR message   (file + console)")
    logger.critical("This is a CRITICAL message (file + console)")

    
    logger2 = setup_logger()
    assert logger is logger2, "setup_logger() returned a different instance!"
    assert len(logger.handlers) == 2, (
        f"Expected 2 handlers, got {len(logger.handlers)}"
    )
    logger.info("Duplicate-call safety verified ✓")

    
    reset_logger()
    logger3 = setup_logger(console_level=logging.DEBUG)
    logger3.debug("After reset, this DEBUG message should appear on console too")
    logger3.info("Reset + reconfigure verified ✓")

    print("\nAll checks passed. See logs/trading_bot.log for full output.")
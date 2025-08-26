#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Configuration Module
Professional logging setup for drone simulator v5.1
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup comprehensive logging for the drone simulator
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_dir: Directory for log files
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_to_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(log_dir, f"drone_simulator_{timestamp}.log")
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_filename,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Error file handler for critical issues
    if log_to_file:
        error_log_filename = os.path.join(log_dir, f"drone_simulator_errors_{timestamp}.log")
        error_handler = logging.FileHandler(error_log_filename, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("🚁 Advanced Drone Swarm Simulator v5.1 - Logging Started")
    logger.info("=" * 60)
    logger.info(f"📝 Log Level: {log_level}")
    logger.info(f"📁 Log Directory: {os.path.abspath(log_dir) if log_to_file else 'Console only'}")
    logger.info(f"💾 Max File Size: {max_file_size / 1024 / 1024:.1f}MB")
    logger.info(f"🔄 Backup Count: {backup_count}")
    
    return logger

def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        module_name: Name of the module
        
    Returns:
        Module-specific logger
    """
    return logging.getLogger(module_name)

def log_performance(func):
    """
    Decorator to log function performance
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance logging
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 0.1:  # Only log if execution takes more than 100ms
                logger.debug(f"⏱️  {func.__name__} executed in {execution_time:.3f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"💥 {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

def log_method_calls(cls):
    """
    Class decorator to log all method calls
    
    Args:
        cls: Class to monitor
        
    Returns:
        Modified class with method call logging
    """
    logger = logging.getLogger(cls.__module__)
    
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(cls, attr_name, log_performance(attr))
    
    logger.debug(f"🔍 Method call logging enabled for {cls.__name__}")
    return cls

class LogContext:
    """Context manager for temporary log level changes"""
    
    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.old_level = None
    
    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)

class CollisionEventFilter(logging.Filter):
    """Custom filter for collision events"""
    
    def filter(self, record):
        # Add collision event marker
        if 'collision' in record.getMessage().lower():
            record.collision_event = True
        return True

def setup_collision_logging(log_dir: str = "logs") -> logging.Logger:
    """
    Setup specialized logging for collision events
    
    Args:
        log_dir: Directory for collision logs
        
    Returns:
        Collision-specific logger
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create collision logger
    collision_logger = logging.getLogger('collision')
    collision_logger.setLevel(logging.DEBUG)
    
    # Collision file handler
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    collision_log_file = os.path.join(log_dir, f"collision_events_{timestamp}.log")
    
    collision_handler = logging.FileHandler(collision_log_file, encoding='utf-8')
    collision_handler.setLevel(logging.DEBUG)
    
    # Collision-specific formatter
    collision_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S.%f'
    )
    collision_handler.setFormatter(collision_formatter)
    
    # Add filter
    collision_filter = CollisionEventFilter()
    collision_handler.addFilter(collision_filter)
    
    collision_logger.addHandler(collision_handler)
    
    collision_logger.info("🔍 Collision event logging initialized")
    
    return collision_logger

def log_system_info():
    """Log system information for debugging"""
    import platform
    import psutil
    
    logger = logging.getLogger(__name__)
    
    logger.info("🖥️  System Information:")
    logger.info(f"   Platform: {platform.system()} {platform.release()}")
    logger.info(f"   Python: {platform.python_version()}")
    logger.info(f"   Architecture: {platform.architecture()[0]}")
    logger.info(f"   Processor: {platform.processor()}")
    
    # Memory information
    memory = psutil.virtual_memory()
    logger.info(f"   Total Memory: {memory.total / 1024**3:.1f}GB")
    logger.info(f"   Available Memory: {memory.available / 1024**3:.1f}GB")
    logger.info(f"   Memory Usage: {memory.percent}%")
    
    # CPU information
    logger.info(f"   CPU Cores: {psutil.cpu_count()}")
    logger.info(f"   CPU Usage: {psutil.cpu_percent(interval=1)}%")

def cleanup_old_logs(log_dir: str = "logs", days_to_keep: int = 30):
    """
    Clean up old log files
    
    Args:
        log_dir: Directory containing log files
        days_to_keep: Number of days of logs to keep
    """
    import glob
    import time
    
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(log_dir):
        return
    
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    deleted_count = 0
    
    for log_file in glob.glob(os.path.join(log_dir, "*.log*")):
        if os.path.getmtime(log_file) < cutoff_time:
            try:
                os.remove(log_file)
                deleted_count += 1
                logger.debug(f"🗑️  Deleted old log file: {log_file}")
            except Exception as e:
                logger.warning(f"Failed to delete log file {log_file}: {e}")
    
    if deleted_count > 0:
        logger.info(f"🧹 Cleaned up {deleted_count} old log files (older than {days_to_keep} days)")

# Example usage and module-level configuration
if __name__ == "__main__":
    # Test logging setup
    logger = setup_logging("DEBUG")
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # Test performance logging
    @log_performance
    def test_function():
        import time
        time.sleep(0.2)
        return "Test result"
    
    result = test_function()
    logger.info(f"Function result: {result}")
    
    # Test collision logging
    collision_logger = setup_collision_logging()
    collision_logger.warning("Test collision event detected")
    
    # Log system info
    log_system_info()
    
    logger.info("Logging test completed")
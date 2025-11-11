"""
Logger utility for Termux PXE Boot
Provides comprehensive logging with different levels and formats
"""
import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_file=None):
        self.log_file = log_file or "/data/data/com.termux/files/home/.termux_pxe_boot/pxe_boot.log"
        self.setup_logger()
        
    def setup_logger(self):
        """Setup the logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger('TermuxPXEBoot')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler (for Termux terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set formatters
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
        
    def info(self, message):
        """Log info message"""
        self.logger.info(f"ℹ️ {message}")
        
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(f"⚠️ {message}")
        
    def error(self, message):
        """Log error message"""
        self.logger.error(f"❌ {message}")
        
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(f"🔥 {message}")
        
    def success(self, message):
        """Log success message (custom level)"""
        self.logger.info(f"✅ {message}")
        
    def start_session(self):
        """Log the start of a new session"""
        self.info("=" * 60)
        self.info("TERMUX PXE BOOT SESSION STARTED")
        self.info(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("=" * 60)
        
    def end_session(self):
        """Log the end of a session"""
        self.info("=" * 60)
        self.info("TERMUX PXE BOOT SESSION ENDED")
        self.info(f"Session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("=" * 60)
        
    def get_log_file_path(self):
        """Get the path to the log file"""
        return self.log_file
        
    def clear_logs(self):
        """Clear the log file"""
        try:
            with open(self.log_file, 'w') as f:
                f.write('')
            self.info("Log file cleared")
        except Exception as e:
            self.error(f"Failed to clear log file: {e}")
            
    def get_recent_logs(self, lines=50):
        """Get recent log entries"""
        try:
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
                return ''.join(log_lines[-lines:])
        except Exception as e:
            self.error(f"Failed to read log file: {e}")
            return ""Logger utility for Termux PXE Boot
Provides comprehensive logging with different levels and formats
"""
import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_file=None):
        self.log_file = log_file or "/data/data/com.termux/files/home/.termux_pxe_boot/pxe_boot.log"
        self.setup_logger()
        
    def setup_logger(self):
        """Setup the logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger('TermuxPXEBoot')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler (for Termux terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set formatters
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
        
    def info(self, message):
        """Log info message"""
        self.logger.info(f"ℹ️ {message}")
        
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(f"⚠️ {message}")
        
    def error(self, message):
        """Log error message"""
        self.logger.error(f"❌ {message}")
        
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(f"🔥 {message}")
        
    def success(self, message):
        """Log success message (custom level)"""
        self.logger.info(f"✅ {message}")
        
    def start_session(self):
        """Log the start of a new session"""
        self.info("=" * 60)
        self.info("TERMUX PXE BOOT SESSION STARTED")
        self.info(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("=" * 60)
        
    def end_session(self):
        """Log the end of a session"""
        self.info("=" * 60)
        self.info("TERMUX PXE BOOT SESSION ENDED")
        self.info(f"Session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("=" * 60)
        
    def get_log_file_path(self):
        """Get the path to the log file"""
        return self.log_file
        
    def clear_logs(self):
        """Clear the log file"""
        try:
            with open(self.log_file, 'w') as f:
                f.write('')
            self.info("Log file cleared")
        except Exception as e:
            self.error(f"Failed to clear log file: {e}")
            
    def get_recent_logs(self, lines=50):
        """Get recent log entries"""
        try:
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
                return ''.join(log_lines[-lines:])
        except Exception as e:
            self.error(f"Failed to read log file: {e}")
            return ""

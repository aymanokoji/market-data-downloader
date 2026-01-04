"""Logging utilities for tracking download failures."""

import os
from datetime import datetime
from market_data.config import LOG_DIR


class DownloadLogger:
    """Logs download attempts and failures for audit trail."""
    
    def __init__(self, log_file: str = None):
        os.makedirs(LOG_DIR, exist_ok=True)
        
        if log_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(LOG_DIR, f'download_{timestamp}.log')
        
        self.log_file = log_file
        self._write_header()
    
    def _write_header(self):
        """Write log file header."""
        with open(self.log_file, 'w') as f:
            f.write(f"Market Data Download Log\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"{'='*60}\n\n")
    
    def log_success(self, ticker: str, action: str, details: str = ""):
        """Log successful download."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp}] SUCCESS | {ticker:8s} | {action:20s} | {details}\n"
        with open(self.log_file, 'a') as f:
            f.write(message)
    
    def log_failure(self, ticker: str, action: str, reason: str):
        """Log failed download."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp}] FAILURE | {ticker:8s} | {action:20s} | {reason}\n"
        with open(self.log_file, 'a') as f:
            f.write(message)
    
    def log_skip(self, ticker: str, reason: str):
        """Log skipped ticker."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp}] SKIP    | {ticker:8s} | {reason}\n"
        with open(self.log_file, 'a') as f:
            f.write(message)
    
    def get_log_path(self) -> str:
        """Return path to log file."""
        return self.log_file
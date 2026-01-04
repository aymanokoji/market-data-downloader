"""File handling utilities."""

import os
import pandas as pd
from datetime import datetime
from typing import Optional
from market_data.config import WINDOWS_RESERVED, DATA_DIR, SPLIT_DIR, DIVIDEND_DIR


class FileHandler:
    """Handles file operations for market data."""
    
    @staticmethod
    def safe_filename(ticker: str) -> str:
        """Convert ticker to Windows-safe filename."""
        if ticker.upper() in WINDOWS_RESERVED:
            return f"{ticker}_ticker"
        return ticker
    
    @staticmethod
    def ensure_directories():
        """Create necessary directories if they don't exist."""
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(SPLIT_DIR, exist_ok=True)
        os.makedirs(DIVIDEND_DIR, exist_ok=True)
    
    @staticmethod
    def get_last_date(ticker: str) -> Optional[datetime]:
        """Get the last date in the ticker's data file."""
        safe_name = FileHandler.safe_filename(ticker)
        file_path = os.path.join(DATA_DIR, f'{safe_name}.csv')
        
        if not os.path.exists(file_path):
            return None
        
        try:
            df = pd.read_csv(file_path)
            if len(df) == 0:
                return None
            last_date_str = df['Date'].iloc[-1]
            return datetime.strptime(last_date_str, '%Y-%m-%d')
        except Exception:
            return None
    
    @staticmethod
    def file_exists(ticker: str) -> bool:
        """Check if data file exists for ticker."""
        safe_name = FileHandler.safe_filename(ticker)
        file_path = os.path.join(DATA_DIR, f'{safe_name}.csv')
        return os.path.exists(file_path)
    
    @staticmethod
    def save_ohlcv(ticker: str, data: str, append: bool = False):
        """Save OHLCV data to CSV."""
        safe_name = FileHandler.safe_filename(ticker)
        file_path = os.path.join(DATA_DIR, f'{safe_name}.csv')
        
        lines = data.strip().split('\n')
        
        mode = 'a' if append else 'w'
        with open(file_path, mode) as f:
            if not append:
                f.write("Date,Open,High,Low,Close,Volume\n")
            
            start_idx = 1  # Skip header
            for line in lines[start_idx:]:
                parts = line.split(',')
                if len(parts) >= 7:  # Ensure we have all fields
                    # EODHD format: Date,Open,High,Low,Close,Adjusted_close,Volume
                    f.write(f"{parts[0]},{parts[1]},{parts[2]},{parts[3]},{parts[4]},{parts[6]}\n")
    
    @staticmethod
    def save_splits(ticker: str, data: str, append: bool = False):
        """Save split data to CSV."""
        safe_name = FileHandler.safe_filename(ticker)
        file_path = os.path.join(SPLIT_DIR, f'{safe_name}.csv')
        
        mode = 'a' if append else 'w'
        with open(file_path, mode) as f:
            if append:
                lines = data.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    f.write(line + '\n')
            else:
                f.write(data)
    
    @staticmethod
    def save_dividends(ticker: str, data: str, append: bool = False):
        """Save dividend data to CSV."""
        safe_name = FileHandler.safe_filename(ticker)
        file_path = os.path.join(DIVIDEND_DIR, f'{safe_name}.csv')
        
        mode = 'a' if append else 'w'
        with open(file_path, mode) as f:
            if append:
                lines = data.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    f.write(line + '\n')
            else:
                f.write(data)
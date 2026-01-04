"""Core downloader logic with single-source policy."""

import threading
from datetime import datetime, timedelta
from typing import Tuple
from market_data.utils import EODHDClient, FileHandler, DownloadLogger


class MarketDataDownloader:
    """
    Downloads and updates market data from EODHD API.
    
    Single-source policy: Only uses EODHD for data integrity.
    Failed downloads are logged for manual review.
    """
    
    def __init__(self, verbose: bool = True, logger: DownloadLogger = None):
        self.verbose = verbose
        self.print_lock = threading.Lock()
        self.logger = logger or DownloadLogger()
        FileHandler.ensure_directories()
    
    def _print(self, message: str):
        """Thread-safe print."""
        if self.verbose:
            with self.print_lock:
                print(message)
    
    def download_ticker(self, ticker: str, index: int, 
                    download_splits: bool, download_dividends: bool) -> Tuple[str, str]:
        """
        Download or update data for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            index: Index for progress tracking
            download_splits: Whether to download split data
            download_dividends: Whether to download dividend data
        
        Returns:
            (ticker, status)
        """
        # Check if file exists
        if not FileHandler.file_exists(ticker):
            return self._download_full_history(ticker, index, download_splits, download_dividends)
        else:
            return self._update_existing(ticker, index, download_splits, download_dividends)
    
    def _download_full_history(self, ticker: str, index: int,
                            download_splits: bool, download_dividends: bool) -> Tuple[str, str]:
        """Download full history for a new ticker."""
        self._print(f"[{index}] {ticker}: Downloading full history...")
        
        # Fetch OHLCV
        success, msg, data = EODHDClient.fetch_ohlcv(ticker)
        
        if not success:
            self._print(f"[{index}] {ticker}: ✗ Failed - {msg}")
            self.logger.log_failure(ticker, "download_ohlcv", msg)
            return ticker, f'error_{msg}'
        
        # Save OHLCV
        try:
            FileHandler.save_ohlcv(ticker, data, append=False)
        except Exception as e:
            self._print(f"[{index}] {ticker}: ✗ Save failed - {str(e)}")
            self.logger.log_failure(ticker, "save_ohlcv", str(e))
            return ticker, f'error_save_{str(e)}'
        
        # Download splits if requested
        if download_splits:
            success_s, msg_s, data_s = EODHDClient.fetch_splits(ticker)
            if success_s:
                FileHandler.save_splits(ticker, data_s, append=False)
                self.logger.log_success(ticker, "download_splits")
            elif msg_s != "Empty response":  # Empty is OK (no splits)
                self.logger.log_failure(ticker, "download_splits", msg_s)
        
        # Download dividends if requested
        if download_dividends:
            success_d, msg_d, data_d = EODHDClient.fetch_dividends(ticker)
            if success_d:
                FileHandler.save_dividends(ticker, data_d, append=False)
                self.logger.log_success(ticker, "download_dividends")
            elif msg_d != "Empty response":  # Empty is OK (no dividends)
                self.logger.log_failure(ticker, "download_dividends", msg_d)
        
        self._print(f"[{index}] {ticker}: ✓ Downloaded")
        self.logger.log_success(ticker, "download_full", "Complete history")
        return ticker, 'downloaded'
    
    def _update_existing(self, ticker: str, index: int,
                        download_splits: bool, download_dividends: bool) -> Tuple[str, str]:
        """Update existing ticker data."""
        last_date = FileHandler.get_last_date(ticker)
        
        if not last_date:
            self._print(f"[{index}] {ticker}: ✗ Invalid existing file")
            self.logger.log_failure(ticker, "update", "Cannot parse existing file")
            return ticker, 'error_invalid_file'
        
        days_diff = (datetime.now() - last_date).days
        
        if days_diff <= 1:
            self._print(f"[{index}] {ticker}: Up to date")
            self.logger.log_skip(ticker, "Already up to date")
            return ticker, 'up_to_date'
        
        start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        self._print(f"[{index}] {ticker}: Updating from {start_date}...")
        
        # Fetch new data
        success, msg, data = EODHDClient.fetch_ohlcv(ticker, start_date, today)
        
        if not success:
            self._print(f"[{index}] {ticker}: ✗ Update failed - {msg}")
            self.logger.log_failure(ticker, "update_ohlcv", msg)
            return ticker, f'error_update_{msg}'
        
        # Parse and save
        lines = data.strip().split('\n')
        num_lines = len(lines) - 1  # Exclude header
        
        if num_lines <= 0:
            self._print(f"[{index}] {ticker}: No new data")
            self.logger.log_skip(ticker, "No new data available")
            return ticker, 'no_new_data'
        
        try:
            FileHandler.save_ohlcv(ticker, data, append=True)
        except Exception as e:
            self._print(f"[{index}] {ticker}: ✗ Save failed - {str(e)}")
            self.logger.log_failure(ticker, "save_update", str(e))
            return ticker, f'error_save_{str(e)}'
        
        # Update splits if requested
        if download_splits:
            success_s, msg_s, data_s = EODHDClient.fetch_splits(ticker, start_date, today)
            if success_s:
                FileHandler.save_splits(ticker, data_s, append=True)
                self.logger.log_success(ticker, "update_splits")
            elif msg_s != "Empty response":
                self.logger.log_failure(ticker, "update_splits", msg_s)
        
        # Update dividends if requested
        if download_dividends:
            success_d, msg_d, data_d = EODHDClient.fetch_dividends(ticker, start_date, today)
            if success_d:
                FileHandler.save_dividends(ticker, data_d, append=True)
                self.logger.log_success(ticker, "update_dividends")
            elif msg_d != "Empty response":
                self.logger.log_failure(ticker, "update_dividends", msg_d)
        
        self._print(f"[{index}] {ticker}: ✓ Updated (+{num_lines} days)")
        self.logger.log_success(ticker, "update", f"+{num_lines} days")
        return ticker, f'updated_{num_lines}'
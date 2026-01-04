"""API client for fetching market data from EODHD."""

import requests
import time
from typing import Tuple, Optional
from market_data.config import EODHD_API_KEY, EODHD_BASE_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY


class EODHDClient:
    """Client for EODHD API with retry logic."""
    
    @staticmethod
    def _fetch_with_retry(url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Fetch data with automatic retry on transient failures.
        
        Returns:
            (success, message, data)
        """
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                
                # Success
                if response.status_code == 200:
                    if len(response.text) < 50:
                        return False, "Empty response", None
                    return True, "Success", response.text
                
                # Permanent errors (don't retry)
                if response.status_code in [400, 401, 403, 404]:
                    return False, f"HTTP {response.status_code}", None
                
                # Transient errors (retry)
                if response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    return False, f"HTTP {response.status_code} (max retries)", None
                
                # Other errors
                return False, f"HTTP {response.status_code}", None
                
            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False, "Timeout", None
                
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False, str(e), None
        
        return False, "Max retries exceeded", None
    
    @staticmethod
    def fetch_ohlcv(ticker: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Fetch OHLCV data from EODHD.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD), None for all history
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            (success, message, data)
        """
        url = f"{EODHD_BASE_URL}/eod/{ticker}.US?period=d&api_token={EODHD_API_KEY}&fmt=csv"
        
        if start_date:
            url += f"&from={start_date}"
        if end_date:
            url += f"&to={end_date}"
        
        return EODHDClient._fetch_with_retry(url)
    
    @staticmethod
    def fetch_splits(ticker: str, start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Fetch stock split data from EODHD."""
        url = f"{EODHD_BASE_URL}/splits/{ticker}.US?period=d&api_token={EODHD_API_KEY}&fmt=csv"
        
        if start_date:
            url += f"&from={start_date}"
        if end_date:
            url += f"&to={end_date}"
        
        return EODHDClient._fetch_with_retry(url)
    
    @staticmethod
    def fetch_dividends(ticker: str, start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Fetch dividend data from EODHD."""
        url = f"{EODHD_BASE_URL}/div/{ticker}.US?period=d&api_token={EODHD_API_KEY}&fmt=csv"
        
        if start_date:
            url += f"&from={start_date}"
        if end_date:
            url += f"&to={end_date}"
        
        return EODHDClient._fetch_with_retry(url)
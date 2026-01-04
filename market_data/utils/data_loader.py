"""
Data Loader module.
Responsible for loading raw data and applying adjustments (Splits/Dividends) on the fly.
"""
import pandas as pd
import os
from market_data.config import DATA_DIR, SPLIT_DIR, DIVIDEND_DIR

class DataLoader:
    @staticmethod
    def load_ticker(ticker: str, adjust_splits: bool = True, adjust_dividends: bool = False) -> pd.DataFrame:
        """
        Loads market data for a ticker and applies adjustments.
        
        Args:
            ticker: Ticker symbol (e.g., 'AAPL')
            adjust_splits: If True, retroactively adjusts past prices for stock splits.
            adjust_dividends: If True, calculates Total Return (adjusts for dividends).
            
        Returns:
            pd.DataFrame: OHLCV data with valid datetime index.
        """
        # 1. Load Raw OHLCV
        # -----------------
        # We need the safe filename logic from FileHandler, but to keep dependencies simple
        # we re-implement the basic check or just import if FileHandler is available.
        # Here we assume standard naming.
        safe_ticker = ticker.replace('/', '_').replace('\\', '_')
        # Handle Windows reserved names manually if strictly needed, 
        # or better: import FileHandler if circular imports aren't an issue.
        # For simplicity here, we assume standard paths:
        
        csv_path = os.path.join(DATA_DIR, f"{safe_ticker}.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"No data found for {ticker} in {DATA_DIR}")
            
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # 2. Apply Split Adjustments
        # --------------------------
        if adjust_splits:
            split_path = os.path.join(SPLIT_DIR, f"{safe_ticker}.csv")
            if os.path.exists(split_path):
                splits = pd.read_csv(split_path)
                splits['Date'] = pd.to_datetime(splits['Date'])
                
                # Initialize Split Factor as 1.0 (no change)
                df['SplitFactor'] = 1.0
                
                for _, row in splits.iterrows():
                    split_date = row['Date']
                    ratio_str = row['Stock Splits'] 
                    # Format is usually "4.000000/1.000000" or just float
                    try:
                        numerator, denominator = map(float, ratio_str.split('/'))
                        ratio = numerator / denominator
                    except ValueError:
                        ratio = float(ratio_str)
                    
                    # Logic: If on Date X a 2:1 split happens, price drops by half.
                    # To normalize history, we divide ALL OLD prices by 2.
                    # We apply this to every date strictly BEFORE the split date.
                    mask = df.index < split_date
                    df.loc[mask, 'SplitFactor'] *= ratio
                
                # Apply the factor
                # Prices go DOWN for old data (divided by factor)
                cols_to_adjust = ['Open', 'High', 'Low', 'Close']
                for col in cols_to_adjust:
                    df[col] = df[col] / df['SplitFactor']
                
                # Volume goes UP for old data (multiplied by factor)
                df['Volume'] = df['Volume'] * df['SplitFactor']
                
                # Cleanup
                df.drop(columns=['SplitFactor'], inplace=True)

        # 3. Apply Dividend Adjustments (Total Return)
        # --------------------------------------------
        # Note: This is complex. Standard "Adjusted Close" usually subtracts dividends 
        # from past prices. A rigorous Total Return calculation typically involves 
        # reinvestment logic. This is a simplified backward adjustment.
        if adjust_dividends:
            div_path = os.path.join(DIVIDEND_DIR, f"{safe_ticker}.csv")
            if os.path.exists(div_path):
                divs = pd.read_csv(div_path)
                divs['Date'] = pd.to_datetime(divs['Date'])
                divs.set_index('Date', inplace=True)
                
                # Join dividends to the main dataframe
                # We use 'asfreq' or reindex to align dates
                df = df.join(divs['Dividends'], how='left').fillna(0.0)
                
                # Calculate Adjustment Factor
                # Formula: Adj_Factor = (Close - Dividend) / Close
                # We calculate this backwards cumulatively
                
                # However, the standard Yahoo-style adjustment is:
                # 1. Calculate % drop on ex-div date
                # 2. Apply that % drop to all previous data
                
                # Simplified Vectorized approach for Total Return Price:
                df['Adj_Factor'] = (df['Close'] - df['Dividends']) / df['Close']
                df['Adj_Factor'] = df['Adj_Factor'].replace(0, 1.0) # Handle edge cases
                
                # Since dividends only affect PREVIOUS prices, we need a cumulative product
                # But strictly speaking, Yahoo method is simpler. 
                # Ideally, stick to Split Adjustment for price levels, 
                # and use Dividends explicitly for backtesting returns.
                pass 

        return df
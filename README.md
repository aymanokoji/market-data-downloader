# Market Data Downloader

Tool for downloading historical market data with a focus on **data integrity** and **reproducibility**.

## Data Philosophy

This project follows a **single-source principle** to ensure data consistency:

- **Primary Source**: EODHD API
- **No Fallbacks**: Failed downloads are logged, not silently replaced
- **Auditability**: All operations are logged with timestamps

### Why Single Source?

In quantitative finance, mixing data sources introduces:
- Price discrepancies between providers
- Inconsistent corporate action adjustments (splits, dividends)
- Non-reproducible research and backtests

## Features

- ✅ Download OHLCV data (unadjusted prices)
- ✅ Download stock splits and dividends
- ✅ Incremental updates (only fetch new data)
- ✅ Multi-threaded downloads (configurable)
- ✅ Automatic retry on transient failures
- ✅ Comprehensive logging for failed downloads
- ✅ Windows-safe filenames (handles CON, PRN, etc.)

## Installation
```bash
# Clone repository
git clone https://github.com/aymanokoji/market-data-downloader.git
cd market_data_downloader

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your EODHD API key
```

## Usage

### Interactive Mode
```bash
python main.py
```

### Command Line Examples

Update all tickers with splits and dividends:
```bash
python main.py --mode all --splits --dividends --threads 100
```

Download single ticker:
```bash
python main.py --mode single --ticker AAPL --splits --dividends
```

Use custom ticker list:
```bash
python main.py --mode all --tickers-file my_tickers.txt --threads 50
```

## File Structure
```
market_data_downloader/
├── .env                   # API Keys & Environment Variables
├── main.py                # Updater Script (Entry Point)
├── setup.py               # Installation script for the library
├── README.md              # Documentation
│
├── market_data/           # 📦 THE LIBRARY (Source Code)
│   ├── config.py          # Configuration & Path Management
│   ├── downloader.py      # Core download logic
│   └── utils/             # Utility modules
│       ├── api_client.py  # EODHD API interactions
│       ├── data_loader.py # Logic for adjusting prices on load
│       ├── file_handler.py
│       └── logger.py
│
└── DATABASE/              # 🗄️ THE STORAGE
    ├── raw_data/          # Raw OHLCV CSVs (Unadjusted)
    ├── split/             # Stock Split history CSVs
    └── dividend/          # Dividend history CSVs
```

## Data Format

### OHLCV (adjusted_data/)
```csv
Date,Open,High,Low,Close,Volume
2024-01-02,187.15,188.44,185.19,185.64,54239900
```

### Splits (split/)
```csv
Date,"Stock Splits"
2020-08-31,4.000000/1.000000
```

### Dividends (dividend/)
```csv
Date,Dividends
2024-02-09,0.24
```

## Handling Failed Downloads

Failed downloads are logged in `logs/download_YYYYMMDD_HHMMSS.log`:
```
[2025-01-05 14:23:45] FAILURE | AAPL     | download_ohlcv       | HTTP 404
[2025-01-05 14:23:46] FAILURE | XYZ      | download_ohlcv       | Timeout
```

**Manual Review Process:**
1. Check log file for failure reasons
2. Verify ticker symbols are correct
3. Check if ticker is delisted or invalid
4. Retry failed tickers individually

## Configuration

Edit `config.py` to customize:
```python
DEFAULT_THREADS = 100        # Concurrent downloads
REQUEST_TIMEOUT = 10         # Request timeout (seconds)
MAX_RETRIES = 3             # Retry attempts
RETRY_DELAY = 2             # Delay between retries
```

## API Rate Limits

EODHD API limits depend on your subscription plan. Adjust `DEFAULT_THREADS` accordingly

## 🚀 Integration in Strategies (How to Load Data)
This engine is designed to be imported directly into your trading strategies. It handles the complexity of merging raw prices with splits and dividends automatically.

You don't need to parse CSVs manually. Use the DataLoader.

1. Basic Import
```Python

from market_data.utils import DataLoader
df = DataLoader.load_ticker("AAPL")
print(df.tail())
```
2. Advanced Loading (Split Adjustment)
By default, the loader provides Adjusted Data (Raw prices corrected for splits and dividends). You can control this behavior:

```Python

# Option A: Get Fully Adjusted Prices (Recommended for Backtesting)
# Applies both Split and Dividend adjustments to OHLCV
df = DataLoader.load_ticker("AAPL", adjust_splits=True, adjust_dividends=True)
# Option B: Get Raw Prices (e.g., for verifying trade execution prices)
df_raw = DataLoader.load_ticker("AAPL", adjust_splits=False, adjust_dividends=False)
```
3. Batch Loading
To load multiple tickers at once (returns a Dictionary of DataFrames):

```Python

tickers = ["AAPL", "MSFT", "GOOGL"]
data_dict = DataLoader.load_tickers(tickers)
# Access specific data
apple_data = data_dict["AAPL"].
```
"""Main entry point for market data downloader."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from market_data.downloader import MarketDataDownloader
from market_data.utils import DownloadLogger
from market_data.config import DEFAULT_THREADS


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Market Data Downloader - Single source (EODHD) for data integrity'
    )
    parser.add_argument('--mode', choices=['all', 'single'], help='Download mode')
    parser.add_argument('--ticker', type=str, help='Single ticker to download')
    parser.add_argument('--splits', action='store_true', help='Download splits')
    parser.add_argument('--dividends', action='store_true', help='Download dividends')
    parser.add_argument('--threads', type=int, default=DEFAULT_THREADS, help='Number of threads')
    parser.add_argument('--tickers-file', type=str, default='tickers.txt', help='Path to tickers file')
    
    return parser.parse_args()


def interactive_mode():
    """Run in interactive mode."""
    print("="*60)
    print("MARKET DATA DOWNLOADER")
    print("Data Source: EODHD (single source policy)")
    print("="*60)
    
    # Mode selection
    while True:
        choice = input("\nMODE:\n  1. Update ALL tickers\n  2. Download SINGLE ticker\nChoice (1/2): ").strip()
        if choice in ['1', '2']:
            single_mode = (choice == '2')
            break
        print("Enter 1 or 2.")
    
    # Get tickers
    if single_mode:
        ticker = input("\nEnter ticker (e.g., AAPL): ").strip().upper()
        tickers = [ticker]
    else:
        try:
            with open('tickers.txt', 'r') as f:
                tickers = [line.strip() for line in f if line.strip()]
            print(f"\nFound {len(tickers)} tickers")
        except FileNotFoundError:
            print("ERROR: tickers.txt not found!")
            return None
    
    # Splits
    while True:
        choice = input("\nDownload SPLITS? (y/n): ").lower().strip()
        if choice in ['y', 'n', 'yes', 'no']:
            download_splits = choice in ['y', 'yes']
            break
    
    # Dividends
    while True:
        choice = input("Download DIVIDENDS? (y/n): ").lower().strip()
        if choice in ['y', 'n', 'yes', 'no']:
            download_dividends = choice in ['y', 'yes']
            break
    
    # Threads
    if not single_mode:
        while True:
            try:
                threads = int(input("\nNumber of threads (1-200): ").strip())
                if 1 <= threads <= 200:
                    break
            except:
                pass
            print("Enter a number between 1 and 200.")
    else:
        threads = 1
    
    return tickers, download_splits, download_dividends, threads


def main():
    """Main function."""
    args = parse_args()
    
    # Determine mode
    if args.mode:
        # Command line mode
        if args.mode == 'single':
            if not args.ticker:
                print("ERROR: --ticker required for single mode")
                return
            tickers = [args.ticker.upper()]
            threads = 1
        else:
            try:
                with open(args.tickers_file, 'r') as f:
                    tickers = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"ERROR: {args.tickers_file} not found!")
                return
            threads = args.threads
        
        download_splits = args.splits
        download_dividends = args.dividends
    else:
        # Interactive mode
        result = interactive_mode()
        if not result:
            return
        tickers, download_splits, download_dividends, threads = result
    
    # Print configuration
    print("\n" + "="*60)
    print("CONFIGURATION")
    print("="*60)
    print(f"Data Source: EODHD API (single source)")
    print(f"Tickers: {len(tickers)}")
    print(f"Splits: {'YES' if download_splits else 'NO'}")
    print(f"Dividends: {'YES' if download_dividends else 'NO'}")
    print(f"Threads: {threads}")
    print("="*60 + "\n")
    
    # Initialize logger and downloader
    logger = DownloadLogger()
    downloader = MarketDataDownloader(verbose=True, logger=logger)
    
    print(f"Log file: {logger.get_log_path()}\n")
    
    # Prepare arguments
    ticker_args = [(ticker, i+1, download_splits, download_dividends) 
                   for i, ticker in enumerate(tickers)]
    
    # Download data
    if threads == 1:
        results = [downloader.download_ticker(*args) for args in ticker_args]
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            results = list(executor.map(lambda x: downloader.download_ticker(*x), ticker_args))
    
    # Summary
    downloaded = sum(1 for _, status in results if status == 'downloaded')
    updated = sum(1 for _, status in results if status.startswith('updated'))
    up_to_date = sum(1 for _, status in results if status == 'up_to_date')
    no_data = sum(1 for _, status in results if status == 'no_new_data')
    errors = sum(1 for _, status in results if status.startswith('error'))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Downloaded:  {downloaded}")
    print(f"Updated:     {updated}")
    print(f"Up to date:  {up_to_date}")
    print(f"No new data: {no_data}")
    print(f"Errors:      {errors}")
    print(f"Total:       {len(tickers)}")
    print("="*60)
    
    if errors > 0:
        print(f"\n⚠️  {errors} ticker(s) failed to download.")
        print(f"Check log file for details: {logger.get_log_path()}")
        print("\nFailed tickers:")
        failed = [ticker for ticker, status in results if status.startswith('error')]
        for i, ticker in enumerate(failed[:20], 1):
            print(f"  {i}. {ticker}")
        if len(failed) > 20:
            print(f"  ... and {len(failed) - 20} more")


if __name__ == "__main__":
    main()
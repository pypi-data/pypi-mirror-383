# Stock Analysis

A Python module for analyzing stock data, including technical indicators, financial fundamentals, and candlestick patterns, using yfinance and saving results to Google Sheets.

## Installation

```bash
pip install yfinance-fetch
```

## Usage

Create a usage script (e.g., `example_usage.py`) and define configuration parameters:

```python

from yfinance_fetch import run_all, process_technical_data, process_financial_data, process_candlestick_patterns

# ====== CONFIGURATION SECTION ======

creds_path          = 'credentials.json'     # Path to Google Sheets API credentials JSON file
spreadsheet_name    = 'Yahoo Finance'        # Target Google Spreadsheet name
worksheet_name      = ['Technical Data', 'Financial Data', 'Candlestick Patterns']  # Worksheet tabs to update

use_csv             = False                  # Set True to use CSV input instead of manual tickers(False True)
csv_url             = 'https://archives.nseindia.com/content/indices/ind_nifty500list.csv'  # Source URL for stock list CSV
# List of manual tickers (used when use_csv=False)
manual_tickers      = ["HDFCBANK.NS", "ICICIBANK.NS", "RELIANCE.NS", "INFY.NS", "BHARTIARTL.NS", "LT.NS", "ITC.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"]

api_failed_retries  = 3                      # Number of retry attempts for failed API calls
batch_size          = 15                     # Number of stocks to process per batch
sleep_time          = 1                      # Sleep time (in seconds) between API requests to avoid rate limits

days_to_check_patterns = 7                   # Days window to scan for candlestick patterns

# ====== RUN PIPELINE ======

# Run all modules (technical, financial, and candlestick pattern analysis)
run_all(creds_path, spreadsheet_name, worksheet_name, use_csv, csv_url, manual_tickers, batch_size, sleep_time, days_to_check_patterns)

# # Process and update Technical Data sheet only
# process_technical_data(creds_path, spreadsheet_name, worksheet_name, use_csv, csv_url, manual_tickers, batch_size, sleep_time, days_to_check_patterns)

# # Process and update Financial Data sheet only
# process_financial_data(creds_path, spreadsheet_name, worksheet_name, use_csv, csv_url, manual_tickers, batch_size, sleep_time)

# # Process and update Candlestick Patterns sheet only
# process_candlestick_patterns(creds_path, spreadsheet_name, worksheet_name, use_csv, csv_url, manual_tickers, batch_size, sleep_time, days_to_check_patterns)

```

## Prerequisites

- Google API credentials JSON file for Google Sheets access.
- Python 3.8 or higher.

## Dependencies

See `requirements.txt` for a full list of dependencies.

## License

MIT License
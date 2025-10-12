import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
from tqdm import tqdm
import ta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
import io
import os
import gspread
import json
import pandas as pd
from google.oauth2.service_account import Credentials
import pytz

def get_nifty_symbols(nifty_url, add_ns_suffix=True):
    """Fetch symbols from the provided CSV URL (e.g., Nifty 50)."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
        response = requests.get(nifty_url, headers=headers)
        if response.status_code == 200:
            csv_content = response.content.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            if 'Symbol' not in df.columns:
                raise ValueError("CSV must have a 'Symbol' column")
            symbols = df['Symbol'].dropna().tolist()
            if add_ns_suffix:
                return [f"{symbol}.NS" for symbol in symbols]
            return symbols
        else:
            print(f"Failed to fetch CSV: Status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return []

def detect_environment():
    """Detects whether running in Google Colab or local environment."""
    try:
        import google.colab
        return "colab"
    except ImportError:
        return "local"

def authenticate_google_sheets(creds_path="credentials.json"):
    """
    Auto-detect environment and authenticate Google Sheets API.
    ✅ Works in both Colab and Local Python.
    """
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    env = detect_environment()
    try:
        # --- CASE 1: Colab Environment ---
        if env == "colab":
            from google.colab import userdata
            creds_json = userdata.get("SERVICE_ACCOUNT_CREDS")
            if creds_json:
                SERVICE_ACCOUNT_CREDS = json.loads(creds_json)
                creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_CREDS, scopes=scope)
                return gspread.authorize(creds)
            else:
                raise FileNotFoundError(
                    "⚠️ Colab detected, but 'SERVICE_ACCOUNT_CREDS' not found in userdata. "
                    "Please add it using: userdata['SERVICE_ACCOUNT_CREDS']"
                )

        # --- CASE 2: Local Environment ---
        elif os.path.exists(creds_path):
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            return gspread.authorize(creds)

        # --- CASE 3: No credentials available ---
        else:
            raise FileNotFoundError(
                f"❌ No valid Google credentials found.\n"
                f"Expected either:\n"
                f"  • Local file: '{creds_path}'\n"
                f"  • OR Colab secret: userdata['SERVICE_ACCOUNT_CREDS']"
            )

    except Exception as e:
        raise RuntimeError(f"Google Sheets authentication failed: {e}")


def save_to_google_sheet(df, worksheet_name, spreadsheet_name,
                         creds_path="credentials.json", add_timestamp=True, clear=True):
    """
    Save a DataFrame to Google Sheets.
    ✅ Automatically handles authentication, creation, clearing, and timestamps.
    """
    try:
        client = authenticate_google_sheets(creds_path)

        # Open or create spreadsheet
        try:
            sheet = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            print(f"🆕 Creating new Google Sheet: {spreadsheet_name}")
            sheet = client.create(spreadsheet_name)
            sheet.share(None, perm_type="anyone", role="writer")

        # Open or create worksheet
        try:
            worksheet = sheet.worksheet(worksheet_name)
            if clear:
                worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="50")

        # Detect environment for IST timestamp
        env = detect_environment()
        if env == "colab":
            tz = pytz.timezone("Asia/Kolkata")
            now = datetime.now(tz).strftime("%d-%b-%Y %I:%M %p")
        else:
            now = datetime.now().strftime("%d-%b-%Y %I:%M %p")

        # Write timestamp and DataFrame
        if add_timestamp and worksheet_name not in ["Error", "Info"]:
            worksheet.update(range_name="A1", values=[[f"Last Updated: {now}"]])
            set_with_dataframe(worksheet, df, row=2, col=1)
        else:
            set_with_dataframe(worksheet, df, row=1, col=1)

        print(f"\n✅ Google Sheet updated: {spreadsheet_name} → {worksheet_name}")

    except Exception as e:
        print(f"❌ Failed to update Google Sheet: {e}")

def load_tickers(use_csv, csv_url, manual_tickers):
    """Load tickers from CSV or manual input."""
    if use_csv:
        return get_nifty_symbols(nifty_url=csv_url)
    if manual_tickers:
        return [ticker.strip() for ticker in manual_tickers]
    return []

def get_stock_info(symbol, api_failed_retries=3):
    """Fetch basic stock information for a stock, handling newly listed stocks."""
    failed_attempts = 0
    while failed_attempts < api_failed_retries:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info or {}  # Handle cases where info might be None
            return {
                'Symbol': symbol.replace(".NS", "") if symbol.endswith(".NS") else symbol,
                'Company Name': info.get('longName', '-'),
                'Sector': info.get('sector', '-'),
                'Industry': info.get('industry', '-'),
                'Country': info.get('country', '-'),
                'Exchange': info.get('exchange', '-'),
                'Market Cap': info.get('marketCap', '-'),
                'Currency': info.get('currency', '-'),
                'Website': info.get('website', '-'),
                'Full Time Employees': info.get('fullTimeEmployees', '-'),
                'Business Summary': info.get('longBusinessSummary', '-')[:500]  # Limit summary length
            }
        except Exception as e:
            failed_attempts += 1
            if failed_attempts < api_failed_retries:
                print(f"⚠️ Retry {failed_attempts}/{api_failed_retries} for {symbol}: {e}")
                time.sleep(1)
            continue
    # Return partial or empty info for failed stocks instead of error
    print(f"⚠️ Partial or no info for {symbol} after {api_failed_retries} attempts")
    return {
        'Symbol': symbol.replace(".NS", "") if symbol.endswith(".NS") else symbol,
        'Company Name': '-',
        'Sector': '-',
        'Industry': '-',
        'Country': '-',
        'Exchange': '-',
        'Market Cap': '-',
        'Currency': '-',
        'Website': '-',
        'Full Time Employees': '-',
        'Business Summary': '-'
    }

# --- Technical Data Functions ---
def get_stock_analysis(symbol, df_daily=None, df_weekly=None, df_monthly=None, api_failed_retries=3):
    """Analyze stock across daily, weekly, monthly timeframes."""
    full_symbol = symbol if symbol.endswith(".NS") or symbol.startswith("^") else f"{symbol}.NS"
    stock = yf.Ticker(full_symbol)
    failed_attempts = 0
    error_message = None

    while failed_attempts < api_failed_retries:
        try:
            # Use provided data if available, otherwise fetch
            df_daily = df_daily if df_daily is not None else stock.history(period='2y', interval='1d')
            df_weekly = df_weekly if df_weekly is not None else stock.history(period='3y', interval='1wk')
            df_monthly = df_monthly if df_monthly is not None else stock.history(period='5y', interval='1mo')

            results = []

            if not df_daily.empty and len(df_daily) >= 50:
                daily_analysis = calculate_indicators(df_daily, 'daily', 50, symbol)
                if daily_analysis:
                    results.append(daily_analysis)

            if not df_weekly.empty and len(df_weekly) >= 20:
                weekly_analysis = calculate_indicators(df_weekly, 'weekly', 20, symbol)
                if weekly_analysis:
                    results.append(weekly_analysis)

            if not df_monthly.empty and len(df_monthly) >= 12:
                monthly_analysis = calculate_indicators(df_monthly, 'monthly', 12, symbol)
                if monthly_analysis:
                    results.append(monthly_analysis)

            if not results:
                results.append({
                    'Symbol': symbol.replace(".NS", "") if symbol.endswith(".NS") else symbol,
                    'Timeframe': 'N/A',
                    'Last_Close': '-',
                    'Daily_Return': '-',
                    'Volume': '-',
                    'SMA_20': '-',
                    'SMA_50': '-',
                    'SMA_200': '-',
                    'EMA_20': '-',
                    'EMA_50': '-',
                    'EMA_200': '-',
                    'RSI': '-',
                    'MACD': '-',
                    'MACD_Signal': '-',
                    'MACD_Hist': '-',
                    'BB_Upper': '-',
                    'BB_Middle': '-',
                    'BB_Lower': '-',
                    'STOCH_K': '-',
                    'STOCH_D': '-',
                    'OBV': '-',
                    'Pivot': '-',
                    'BC': '-',
                    'TC': '-',
                    'R1': '-',
                    'S1': '-',
                    'R2': '-',
                    'S2': '-',
                    'R3': '-',
                    'S3': '-',
                    'R4': '-',
                    'S4': '-',
                    'Signals': 'Insufficient historical data (lacks 2-year, 3-year, or 5-year data)'
                })

            return results

        except Exception as e:
            failed_attempts += 1
            error_message = str(e)
            if failed_attempts < api_failed_retries:
                print(f"⚠️ Retry {failed_attempts}/{api_failed_retries} for {symbol}: {e}")
                time.sleep(1)
            continue

    print(f"❌ Failed to analyze {symbol} after {api_failed_retries} attempts: {error_message}")
    return {"symbol": symbol, "error": error_message}

def calculate_indicators(df, timeframe, min_length, symbol):
    """Calculate technical indicators for a given DataFrame."""
    try:
        if len(df) < min_length:
            return None

        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200) if len(df) >= 200 else pd.Series([None] * len(df), index=df.index)
        df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
        df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=50)
        df['EMA_200'] = ta.trend.ema_indicator(df['Close'], window=200) if len(df) >= 200 else pd.Series([None] * len(df), index=df.index)

        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()

        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Middle'] = bb.bollinger_mavg()
        df['BB_Lower'] = bb.bollinger_lband()

        stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        df['STOCH_K'] = stoch.stoch()
        df['STOCH_D'] = stoch.stoch_signal()

        df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()

        prev = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
        prev_high = prev['High']
        prev_low = prev['Low']
        prev_close = prev['Close']

        pivot = (prev_high + prev_low + prev_close) / 3
        bc = (prev_high + prev_low) / 2
        tc = (pivot * 2) - bc

        if tc < bc:
            bc, tc = tc, bc

        r1 = (2 * pivot) - prev_low
        s1 = (2 * pivot) - prev_high
        r2 = pivot + (r1 - s1)
        s2 = pivot - (r1 - s1)
        r3 = prev_high + 2 * (pivot - prev_low)
        s3 = prev_low - 2 * (prev_high - pivot)
        r4 = prev_high + 3 * (pivot - prev_low)
        s4 = prev_low - 3 * (prev_high - pivot)

        latest = df.iloc[-1]

        return {
            'Symbol': symbol.replace(".NS", "") if symbol.endswith(".NS") else symbol,
            'Timeframe': timeframe,
            'Last_Close': round(latest['Close'], 2),
            'Daily_Return': round(((latest['Close'] - prev['Close']) / prev['Close']) * 100, 2) if len(df) > 1 else 0.0,
            'Volume': int(latest['Volume']),
            'SMA_20': round(latest['SMA_20'], 2) if pd.notnull(latest['SMA_20']) else None,
            'SMA_50': round(latest['SMA_50'], 2) if pd.notnull(latest['SMA_50']) else None,
            'SMA_200': round(latest['SMA_200'], 2) if pd.notnull(latest['SMA_200']) else None,
            'EMA_20': round(latest['EMA_20'], 2) if pd.notnull(latest['EMA_20']) else None,
            'EMA_50': round(latest['EMA_50'], 2) if pd.notnull(latest['EMA_50']) else None,
            'EMA_200': round(latest['EMA_200'], 2) if pd.notnull(latest['EMA_200']) else None,
            'RSI': round(latest['RSI'], 2) if pd.notnull(latest['RSI']) else None,
            'MACD': round(latest['MACD'], 2) if pd.notnull(latest['MACD']) else None,
            'MACD_Signal': round(latest['MACD_Signal'], 2) if pd.notnull(latest['MACD_Signal']) else None,
            'MACD_Hist': round(latest['MACD_Hist'], 2) if pd.notnull(latest['MACD_Hist']) else None,
            'BB_Upper': round(latest['BB_Upper'], 2) if pd.notnull(latest['BB_Upper']) else None,
            'BB_Middle': round(latest['BB_Middle'], 2) if pd.notnull(latest['BB_Middle']) else None,
            'BB_Lower': round(latest['BB_Lower'], 2) if pd.notnull(latest['BB_Lower']) else None,
            'STOCH_K': round(latest['STOCH_K'], 2) if pd.notnull(latest['STOCH_K']) else None,
            'STOCH_D': round(latest['STOCH_D'], 2) if pd.notnull(latest['STOCH_D']) else None,
            'OBV': int(latest['OBV']) if pd.notnull(latest['OBV']) else None,
            'Pivot': round(pivot, 2),
            'BC': round(bc, 2),
            'TC': round(tc, 2),
            'R1': round(r1, 2),
            'S1': round(s1, 2),
            'R2': round(r2, 2),
            'S2': round(s2, 2),
            'R3': round(r3, 2),
            'S3': round(s3, 2),
            'R4': round(r4, 2),
            'S4': round(s4, 2),
            'Signals': get_signals(latest, symbol)
        }
    except Exception as e:
        print(f"⚠️ Error calculating indicators for {symbol} ({timeframe}): {e}")
        return None

def get_signals(data, symbol):
    """Generate signal interpretations."""
    signals = []
    if pd.notnull(data['SMA_20']) and pd.notnull(data['SMA_50']):
        signals.append("Bullish MA Crossover" if data['SMA_20'] > data['SMA_50'] else "Bearish MA Crossover")
    if pd.notnull(data['RSI']):
        if data['RSI'] > 70:
            signals.append("Overbought (RSI)")
        elif data['RSI'] < 30:
            signals.append("Oversold (RSI)")
    if pd.notnull(data['MACD']) and pd.notnull(data['MACD_Signal']):
        signals.append("Bullish MACD" if data['MACD'] > data['MACD_Signal'] else "Bearish MACD")
    if pd.notnull(data['BB_Upper']) and pd.notnull(data['Close']):
        if data['Close'] > data['BB_Upper']:
            signals.append("Overbought (BB)")
        elif data['Close'] < data['BB_Lower']:
            signals.append("Oversold (BB)")
    return "; ".join(signals) if signals else "No clear signals"

# --- Financial Data Functions ---
def get_stock_data(symbol, df_1y=None, api_failed_retries=3):
    """Fetch financial data and fundamentals for a stock."""
    failed_attempts = 0
    error_message = None

    while failed_attempts < api_failed_retries:
        try:
            stock = yf.Ticker(symbol)
            # Use provided 1-year data for percentage changes if available
            price_data = df_1y if df_1y is not None else stock.history(period='1y')

            info = stock.info

            if not price_data.empty:
                latest_price = round(price_data.iloc[-1]['Close'], 2)
                volume = int(price_data.iloc[-1]['Volume'])
                daily_change = round(((price_data.iloc[-1]['Close'] - price_data.iloc[-2]['Close']) / price_data.iloc[-2]['Close']) * 100, 2) if len(price_data) > 1 else '-'
                weekly_change = round(((price_data.iloc[-1]['Close'] - price_data.iloc[-6]['Close']) / price_data.iloc[-6]['Close']) * 100, 2) if len(price_data) > 5 else '-'
                monthly_change = round(((price_data.iloc[-1]['Close'] - price_data.iloc[-22]['Close']) / price_data.iloc[-22]['Close']) * 100, 2) if len(price_data) > 21 else '-'
            else:
                latest_price = '-'
                volume = '-'
                daily_change = '-'
                weekly_change = '-'
                monthly_change = '-'

            return {
                'Symbol': symbol.replace(".NS", "") if symbol.endswith(".NS") else symbol,
                'Company Name': info.get('longName', '-'),
                'Sector': info.get('sector', '-'),
                'Industry': info.get('industry', '-'),
                'Market Cap': info.get('marketCap', '-'),
                'PE Ratio': info.get('trailingPE', '-'),
                'Forward PE': info.get('forwardPE', '-'),
                'PEG Ratio': info.get('pegRatio', '-'),
                'Price to Book': info.get('priceToBook', '-'),
                'EV/EBITDA': info.get('enterpriseToEbitda', '-'),
                'Profit Margin': info.get('profitMargins', '-'),
                'Operating Margin': info.get('operatingMargins', '-'),
                'ROE': info.get('returnOnEquity', '-'),
                'ROA': info.get('returnOnAssets', '-'),
                'Revenue': info.get('totalRevenue', '-'),
                'Revenue Per Share': info.get('revenuePerShare', '-'),
                'Quarterly Revenue Growth': info.get('quarterlyRevenueGrowth', '-'),
                'Gross Profit': info.get('grossProfits', '-'),
                'EBITDA': info.get('ebitda', '-'),
                'Net Income': info.get('netIncomeToCommon', '-'),
                'EPS': info.get('trailingEps', '-'),
                'Quarterly Earnings Growth': info.get('quarterlyEarningsGrowth', '-'),
                'Total Cash': info.get('totalCash', '-'),
                'Total Debt': info.get('totalDebt', '-'),
                'Debt To Equity': info.get('debtToEquity', '-'),
                'Current Ratio': info.get('currentRatio', '-'),
                'Book Value': info.get('bookValue', '-'),
                'Free Cash Flow': info.get('freeCashflow', '-'),
                'Dividend Rate': info.get('dividendRate', '-'),
                'Dividend Yield': info.get('dividendYield', '-'),
                'Payout Ratio': info.get('payoutRatio', '-'),
                'Beta': info.get('beta', '-'),
                '52 Week High': info.get('fiftyTwoWeekHigh', '-'),
                '52 Week Low': info.get('fiftyTwoWeekLow', '-'),
                '50 Day Average': info.get('fiftyDayAverage', '-'),
                '200 Day Average': info.get('twoHundredDayAverage', '-'),
                'Latest Price': latest_price,
                'Daily Change %': daily_change if isinstance(daily_change, str) else f"{daily_change:.2f}%",
                'Weekly Change %': weekly_change if isinstance(weekly_change, str) else f"{weekly_change:.2f}%",
                'Monthly Change %': monthly_change if isinstance(monthly_change, str) else f"{monthly_change:.2f}%",
                'Volume': volume,
            }
        except Exception as e:
            failed_attempts += 1
            error_message = str(e)
            if failed_attempts < api_failed_retries:
                print(f"⚠️ Retry {failed_attempts}/{api_failed_retries} for {symbol}: {e}")
                time.sleep(1)
            continue

    print(f"❌ Failed to fetch data for {symbol} after {api_failed_retries} attempts: {error_message}")
    return {"symbol": symbol, "error": error_message}

def process_financial_data(creds_path, spreadsheet_name, worksheet_name, use_csv, csv_url, manual_tickers, batch_size, sleep_time):
    """Process financial data for specified stocks."""
    symbols = load_tickers(use_csv, csv_url, manual_tickers)
    all_stock_data = []
    failed_stocks = []

    print("🔄 Fetching financial data from Yahoo!...\n")
    for i, symbol in enumerate(tqdm(symbols, desc="📊 Progress", ncols=100)):
        data = get_stock_data(symbol)
        if isinstance(data, dict) and "error" in data:
            failed_stocks.append(data)
        elif data:
            all_stock_data.append(data)
        if (i + 1) % batch_size == 0:
            time.sleep(sleep_time)

    # Save financial data
    if all_stock_data:
        df = pd.DataFrame(all_stock_data)
        save_to_google_sheet(df, worksheet_name=worksheet_name[1], creds_path=creds_path, spreadsheet_name=spreadsheet_name)
    else:
        print("❌ No financial data fetched")

    # Save failed stocks
    if failed_stocks:
        df_failed = pd.DataFrame(failed_stocks)
        save_to_google_sheet(df_failed, worksheet_name="Error", creds_path=creds_path, spreadsheet_name=spreadsheet_name, add_timestamp=False)

# --- Candlestick Patterns Functions ---
def detect_candlestick_patterns(df):
    """Detect candlestick patterns for the latest candles."""
    pattern_columns = [
        'Doji', 'Hammer', 'Inverted_Hammer', 'Dragonfly_Doji', 'Spinning_Top',
        'Hanging_Man', 'Shooting_Star', 'Gravestone_Doji', 'Marubozu',
        'Bullish_Kicker', 'Bullish_Engulfing', 'Bullish_Harami', 'Piercing_Line',
        'Tweezer_Bottom', 'Bearish_Kicker', 'Bearish_Engulfing', 'Bearish_Harami',
        'Dark_Cloud_Cover', 'Tweezer_Top', 'Morning_Star', 'Morning_Doji_Star',
        'Bullish_Abandoned_Baby', 'Three_White_Soldiers', 'Three_Line_Strike_Bullish',
        'Three_Inside_Up', 'Three_Outside_Up', 'Evening_Star', 'Evening_Doji_Star',
        'Bearish_Abandoned_Baby', 'Three_Black_Crows', 'Three_Line_Strike_Bearish',
        'Three_Inside_Down', 'Three_Outside_Down'
    ]
    for pattern in pattern_columns:
        df[pattern] = False

    df['Body'] = abs(df['Close'] - df['Open'])
    df['Upper_Shadow'] = df['High'] - df[['Open', 'Close']].max(axis=1)
    df['Lower_Shadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']
    df['Range'] = df['High'] - df['Low']
    epsilon = 0.0001

    latest = df.index[-1]
    df.loc[latest, 'Doji'] = (df.loc[latest, 'Body'] <= 0.05 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Range'] > epsilon)
    df.loc[latest, 'Hammer'] = (df.loc[latest, 'Body'] <= 0.2 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Lower_Shadow'] >= 2.5 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Upper_Shadow'] <= 0.05 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (len(df) >= 2 and df.loc[latest, 'Close'] > df.loc[df.index[-2], 'Close'])
    df.loc[latest, 'Inverted_Hammer'] = (df.loc[latest, 'Body'] <= 0.2 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Upper_Shadow'] >= 2.5 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Lower_Shadow'] <= 0.05 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (len(df) >= 2 and df.loc[latest, 'Close'] > df.loc[df.index[-2], 'Close'])
    df.loc[latest, 'Dragonfly_Doji'] = (df.loc[latest, 'Body'] <= 0.05 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Lower_Shadow'] > 2.5 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Upper_Shadow'] < 0.05 * (df.loc[latest, 'Body'] + epsilon))
    df.loc[latest, 'Spinning_Top'] = (df.loc[latest, 'Body'] <= 0.25 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Upper_Shadow'] > 0.6 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Lower_Shadow'] > 0.6 * (df.loc[latest, 'Body'] + epsilon))
    df.loc[latest, 'Hanging_Man'] = (df.loc[latest, 'Body'] <= 0.2 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Lower_Shadow'] >= 2.5 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Upper_Shadow'] <= 0.05 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (len(df) >= 2 and df.loc[latest, 'Close'] < df.loc[df.index[-2], 'Close'])
    df.loc[latest, 'Shooting_Star'] = (df.loc[latest, 'Body'] <= 0.2 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Upper_Shadow'] >= 2.5 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Lower_Shadow'] <= 0.05 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (len(df) >= 2 and df.loc[latest, 'Close'] < df.loc[df.index[-2], 'Close'])
    df.loc[latest, 'Gravestone_Doji'] = (df.loc[latest, 'Body'] <= 0.05 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Upper_Shadow'] > 2.5 * (df.loc[latest, 'Body'] + epsilon)) & (df.loc[latest, 'Lower_Shadow'] < 0.05 * (df.loc[latest, 'Body'] + epsilon))
    df.loc[latest, 'Marubozu'] = (df.loc[latest, 'Upper_Shadow'] <= 0.05 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Lower_Shadow'] <= 0.05 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[latest, 'Body'] > 0.8 * (df.loc[latest, 'Range'] + epsilon))

    if len(df) >= 2:
        second_last = df.index[-2]
        df.loc[latest, 'Bullish_Kicker'] = (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] > df.loc[second_last, 'Close'] + 0.005 * df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] > df.loc[second_last, 'Open'])
        df.loc[latest, 'Bearish_Kicker'] = (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] < df.loc[second_last, 'Close'] - 0.005 * df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] < df.loc[second_last, 'Open'])
        df.loc[latest, 'Bullish_Engulfing'] = (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] <= df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] >= df.loc[second_last, 'Open']) & (df.loc[latest, 'Body'] > df.loc[second_last, 'Body'])
        df.loc[latest, 'Bearish_Engulfing'] = (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] >= df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] <= df.loc[second_last, 'Open']) & (df.loc[latest, 'Body'] > df.loc[second_last, 'Body'])
        df.loc[latest, 'Bullish_Harami'] = (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] >= df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] <= df.loc[second_last, 'Close']) & (df.loc[latest, 'Body'] < df.loc[second_last, 'Body'])
        df.loc[latest, 'Bearish_Harami'] = (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] <= df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] >= df.loc[second_last, 'Open']) & (df.loc[latest, 'Body'] < df.loc[second_last, 'Body'])
        df.loc[latest, 'Piercing_Line'] = (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] < df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] > (df.loc[second_last, 'Open'] + df.loc[second_last, 'Close']) / 2) & (df.loc[latest, 'Close'] < df.loc[second_last, 'Open'])
        df.loc[latest, 'Dark_Cloud_Cover'] = (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] > df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] < (df.loc[second_last, 'Open'] + df.loc[second_last, 'Close']) / 2) & (df.loc[latest, 'Close'] > df.loc[second_last, 'Open'])
        df.loc[latest, 'Tweezer_Bottom'] = (abs(df.loc[second_last, 'Low'] - df.loc[latest, 'Low']) <= 0.01 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open'])
        df.loc[latest, 'Tweezer_Top'] = (abs(df.loc[second_last, 'High'] - df.loc[latest, 'High']) <= 0.01 * (df.loc[latest, 'Range'] + epsilon)) & (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open'])

    if len(df) >= 3:
        third_last = df.index[-3]
        second_last = df.index[-2]
        df.loc[latest, 'Morning_Star'] = (df.loc[third_last, 'Close'] < df.loc[third_last, 'Open']) & (df.loc[second_last, 'Body'] <= 0.2 * (df.loc[second_last, 'Range'] + epsilon)) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Close'] > (df.loc[third_last, 'Open'] + df.loc[third_last, 'Close']) / 2) & (df.loc[second_last, 'Close'] < df.loc[third_last, 'Close'])
        df.loc[latest, 'Morning_Doji_Star'] = (df.loc[third_last, 'Close'] < df.loc[third_last, 'Open']) & (df.loc[second_last, 'Body'] <= 0.05 * (df.loc[second_last, 'Range'] + epsilon)) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Close'] > (df.loc[third_last, 'Open'] + df.loc[third_last, 'Close']) / 2) & (df.loc[second_last, 'Close'] < df.loc[third_last, 'Close'])
        df.loc[latest, 'Bullish_Abandoned_Baby'] = (df.loc[third_last, 'Close'] < df.loc[third_last, 'Open']) & (df.loc[second_last, 'Body'] <= 0.05 * (df.loc[second_last, 'Range'] + epsilon)) & (df.loc[second_last, 'High'] < df.loc[third_last, 'Low']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Low'] > df.loc[second_last, 'High'])
        df.loc[latest, 'Three_White_Soldiers'] = (df.loc[third_last, 'Close'] > df.loc[third_last, 'Open']) & (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] > df.loc[second_last, 'Close'] - 0.1 * (df.loc[second_last, 'Range'] + epsilon)) & (df.loc[second_last, 'Open'] > df.loc[third_last, 'Close'] - 0.1 * (df.loc[third_last, 'Range'] + epsilon)) & (df.loc[latest, 'Close'] > df.loc[second_last, 'Close']) & (df.loc[second_last, 'Close'] > df.loc[third_last, 'Close'])
        df.loc[latest, 'Three_Line_Strike_Bullish'] = (df.loc[third_last, 'Close'] > df.loc[third_last, 'Open']) & (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Close'] < df.loc[third_last, 'Open']) & (df.loc[latest, 'Open'] > df.loc[second_last, 'Close'])
        df.loc[latest, 'Three_Inside_Up'] = (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] >= df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] <= df.loc[second_last, 'Close']) & (df.loc[third_last, 'Close'] < df.loc[third_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[second_last, 'Open'])
        df.loc[latest, 'Three_Outside_Up'] = (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] <= df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] >= df.loc[second_last, 'Open']) & (df.loc[third_last, 'Close'] < df.loc[third_last, 'Open']) & (df.loc[latest, 'Close'] > df.loc[second_last, 'Close'])
        df.loc[latest, 'Evening_Star'] = (df.loc[third_last, 'Close'] > df.loc[third_last, 'Open']) & (df.loc[second_last, 'Body'] <= 0.2 * (df.loc[second_last, 'Range'] + epsilon)) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Close'] < (df.loc[third_last, 'Open'] + df.loc[third_last, 'Close']) / 2) & (df.loc[second_last, 'Close'] > df.loc[third_last, 'Close'])
        df.loc[latest, 'Evening_Doji_Star'] = (df.loc[third_last, 'Close'] > df.loc[third_last, 'Open']) & (df.loc[second_last, 'Body'] <= 0.05 * (df.loc[second_last, 'Range'] + epsilon)) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Close'] < (df.loc[third_last, 'Open'] + df.loc[third_last, 'Close']) / 2) & (df.loc[second_last, 'Close'] > df.loc[third_last, 'Close'])
        df.loc[latest, 'Bearish_Abandoned_Baby'] = (df.loc[third_last, 'Close'] > df.loc[third_last, 'Open']) & (df.loc[second_last, 'Body'] <= 0.05 * (df.loc[second_last, 'Range'] + epsilon)) & (df.loc[second_last, 'Low'] > df.loc[third_last, 'High']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'High'] < df.loc[second_last, 'Low'])
        df.loc[latest, 'Three_Black_Crows'] = (df.loc[third_last, 'Close'] < df.loc[third_last, 'Open']) & (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] < df.loc[second_last, 'Close'] + 0.1 * (df.loc[second_last, 'Range'] + epsilon)) & (df.loc[second_last, 'Open'] < df.loc[third_last, 'Close'] + 0.1 * (df.loc[third_last, 'Range'] + epsilon)) & (df.loc[latest, 'Close'] < df.loc[second_last, 'Close']) & (df.loc[second_last, 'Close'] < df.loc[third_last, 'Close'])
        df.loc[latest, 'Three_Line_Strike_Bearish'] = (df.loc[third_last, 'Close'] < df.loc[third_last, 'Open']) & (df.loc[second_last, 'Close'] < df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Close'] > df.loc[third_last, 'Open']) & (df.loc[latest, 'Open'] < df.loc[second_last, 'Close'])
        df.loc[latest, 'Three_Inside_Down'] = (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] <= df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] >= df.loc[second_last, 'Open']) & (df.loc[third_last, 'Close'] > df.loc[third_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[second_last, 'Open'])
        df.loc[latest, 'Three_Outside_Down'] = (df.loc[second_last, 'Close'] > df.loc[second_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[latest, 'Open']) & (df.loc[latest, 'Open'] >= df.loc[second_last, 'Close']) & (df.loc[latest, 'Close'] <= df.loc[second_last, 'Open']) & (df.loc[third_last, 'Close'] > df.loc[third_last, 'Open']) & (df.loc[latest, 'Close'] < df.loc[second_last, 'Close'])

    return df.loc[[latest]]

def fetch_yfinance_data(ticker, days, interval='1d', for_technical=False, api_failed_retries=3):
    """Fetch OHLC data for a ticker."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    stock = yf.Ticker(ticker)
    failed_attempts = 0
    error_message = None

    while failed_attempts < api_failed_retries:
        try:
            period = '2y' if for_technical else str(days) + 'd'
            df = stock.history(period=period if for_technical else None, start=start_date if not for_technical else None, end=end_date, interval=interval)
            if df.empty or len(df) < (50 if for_technical else 3):
                error_message = f"No sufficient data for {ticker}. Rows: {len(df)}"
                failed_attempts += 1
                if failed_attempts < api_failed_retries:
                    print(f"⚠️ Retry {failed_attempts}/{api_failed_retries} for {ticker}: {error_message}")
                    time.sleep(1)
                continue
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            return df
        except Exception as e:
            failed_attempts += 1
            error_message = str(e)
            if failed_attempts < api_failed_retries:
                print(f"⚠️ Retry {failed_attempts}/{api_failed_retries} for {ticker}: {e}")
                time.sleep(1)
            continue

    print(f"❌ Failed to fetch data for {ticker} after {api_failed_retries} attempts: {error_message}")
    return {"symbol": ticker, "error": error_message}

def process_technical_data(creds_path, spreadsheet_name, worksheet_name, use_csv, csv_url, manual_tickers, batch_size, sleep_time, days_to_check_patterns):
    """Process technical data for specified stocks."""
    symbols = load_tickers(use_csv, csv_url, manual_tickers)
    technical_results = []
    failed_stocks = []

    print("🔄 Processing Technical Data from Yahoo! Finance...\n")
    for i, symbol in enumerate(tqdm(symbols, desc="📊 Progress", ncols=100)):
        full_symbol = symbol if symbol.endswith(".NS") or symbol.startswith("^") else f"{symbol}.NS"
        
        # Fetch fresh data for technical analysis
        df_daily = fetch_yfinance_data(full_symbol, days=730, for_technical=True, api_failed_retries=3)
        
        if isinstance(df_daily, dict) and "error" in df_daily:
            failed_stocks.append(df_daily)
            continue
        
        # Process technical data
        if df_daily is not None:
            technical_result = get_stock_analysis(symbol, df_daily=df_daily, api_failed_retries=3)
            if isinstance(technical_result, dict) and "error" in technical_result:
                failed_stocks.append(technical_result)
            elif technical_result:
                technical_results.extend(technical_result)

        if (i + 1) % batch_size == 0:
            time.sleep(sleep_time)

    # Save technical data
    if technical_results:
        df_technical = pd.DataFrame(technical_results)
        save_to_google_sheet(df_technical, worksheet_name=worksheet_name[0], creds_path=creds_path, spreadsheet_name=spreadsheet_name)
    else:
        print("❌ No successful technical analyses")

    # Save failed stocks
    if failed_stocks:
        df_failed = pd.DataFrame(failed_stocks)
        save_to_google_sheet(df_failed, worksheet_name="Error", creds_path=creds_path, spreadsheet_name=spreadsheet_name, add_timestamp=False)

def process_candlestick_patterns(creds_path, spreadsheet_name, worksheet_name, use_csv, csv_url, manual_tickers, batch_size, sleep_time, days_to_check_patterns):
    """Process candlestick patterns for stocks."""
    tickers = load_tickers(use_csv, csv_url, manual_tickers)
    if not tickers:
        print("No valid tickers provided.")
        return

    results = []
    failed_stocks = []

    print("🔄 Processing Candlestick Patterns from Yahoo! Finance...\n")
    for i, ticker in enumerate(tqdm(tickers, desc="📊 Progress", unit="ticker", ncols=100)):
        df = fetch_yfinance_data(ticker, days=days_to_check_patterns, api_failed_retries=3)
        if isinstance(df, dict) and "error" in df:
            failed_stocks.append(df)
            continue
        if df is not None:
            df = detect_candlestick_patterns(df)
            clean_ticker = ticker.replace('.NS', '') if ticker.endswith('.NS') else ticker
            df['Ticker'] = clean_ticker
            df['Date'] = df.index.strftime('%Y-%m-%d')
            results.append(df)
        if (i + 1) % batch_size == 0:
            time.sleep(sleep_time)

    if results:
        combined_df = pd.concat([df for df in results if not df.empty])
        pattern_columns = [
            'Doji', 'Hammer', 'Inverted_Hammer', 'Dragonfly_Doji', 'Spinning_Top',
            'Hanging_Man', 'Shooting_Star', 'Gravestone_Doji', 'Marubozu',
            'Bullish_Kicker', 'Bullish_Engulfing', 'Bullish_Harami', 'Piercing_Line',
            'Tweezer_Bottom', 'Bearish_Kicker', 'Bearish_Engulfing', 'Bearish_Harami',
            'Dark_Cloud_Cover', 'Tweezer_Top', 'Morning_Star', 'Morning_Doji_Star',
            'Bullish_Abandoned_Baby', 'Three_White_Soldiers', 'Three_Line_Strike_Bullish',
            'Three_Inside_Up', 'Three_Outside_Up', 'Evening_Star', 'Evening_Doji_Star',
            'Bearish_Abandoned_Baby', 'Three_Black_Crows', 'Three_Line_Strike_Bearish',
            'Three_Inside_Down', 'Three_Outside_Down'
        ]
        combined_df = combined_df[combined_df[pattern_columns].any(axis=1)]
        combined_df[pattern_columns] = combined_df[pattern_columns].map(lambda x: x if x else '-')
        result_df = combined_df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close'] + pattern_columns]
        # print(f"\nCandlestick Patterns for Latest Date:")
        # print(result_df)
        save_to_google_sheet(result_df, worksheet_name=worksheet_name[2], creds_path=creds_path, spreadsheet_name=spreadsheet_name, add_timestamp=False)
    else:
        print("No patterns detected. Check data availability or adjust pattern thresholds.")

    if failed_stocks:
        df_failed = pd.DataFrame(failed_stocks)
        save_to_google_sheet(df_failed, worksheet_name="Error", creds_path=creds_path, spreadsheet_name=spreadsheet_name, add_timestamp=False)

def run_all(creds_path, spreadsheet_name, worksheet_name, use_csv, csv_url, manual_tickers, batch_size, sleep_time, days_to_check_patterns):
    """Run all analyses: stock info, technical, financial, and candlestick patterns with fresh data fetches."""
    symbols = load_tickers(use_csv, csv_url, manual_tickers)
    info_results = []
    technical_results = []
    financial_results = []
    patterns_results = []
    failed_stocks = []

    print("🔄 Running All Analyses from Yahoo! Finance...\n")
    for i, symbol in enumerate(tqdm(symbols, desc="📊 Progress", ncols=100)):
        full_symbol = symbol if symbol.endswith(".NS") or symbol.startswith("^") else f"{symbol}.NS"
        
        # Fetch stock info (no errors added to failed_stocks)
        info_result = get_stock_info(full_symbol, api_failed_retries=3)
        info_results.append(info_result)

        # Fetch fresh data for technical analysis
        df_technical = fetch_yfinance_data(full_symbol, days=730, for_technical=True, api_failed_retries=3)
        if isinstance(df_technical, dict) and "error" in df_technical:
            failed_stocks.append(df_technical)
            continue

        # Process technical data
        if df_technical is not None:
            technical_result = get_stock_analysis(symbol, df_daily=df_technical, api_failed_retries=3)
            if isinstance(technical_result, dict) and "error" in technical_result:
                failed_stocks.append(technical_result)
            elif technical_result:
                technical_results.extend(technical_result)

        # Fetch fresh data for financial percentage changes
        df_financial = fetch_yfinance_data(full_symbol, days=252, api_failed_retries=3)
        if isinstance(df_financial, dict) and "error" in df_financial:
            failed_stocks.append(df_financial)
            continue

        # Process financial data
        if df_financial is not None:
            financial_result = get_stock_data(symbol, df_1y=df_financial, api_failed_retries=3)
            if isinstance(financial_result, dict) and "error" in financial_result:
                failed_stocks.append(financial_result)
            elif financial_result:
                financial_results.append(financial_result)

        # Fetch fresh data for candlestick patterns
        df_patterns = fetch_yfinance_data(full_symbol, days=days_to_check_patterns, api_failed_retries=3)
        if isinstance(df_patterns, dict) and "error" in df_patterns:
            failed_stocks.append(df_patterns)
            continue

        # Process candlestick patterns
        if df_patterns is not None:
            df_patterns = df_patterns.tail(3)[['Open', 'High', 'Low', 'Close']].copy()
            df_patterns = detect_candlestick_patterns(df_patterns)
            clean_ticker = symbol.replace(".NS", "") if symbol.endswith(".NS") else symbol
            df_patterns['Ticker'] = clean_ticker
            df_patterns['Date'] = df_patterns.index.strftime('%Y-%m-%d')
            patterns_results.append(df_patterns)

        if (i + 1) % batch_size == 0:
            time.sleep(sleep_time)

    # Save stock info
    if info_results:
        df_info = pd.DataFrame(info_results)
        save_to_google_sheet(df_info, worksheet_name="Info", creds_path=creds_path, spreadsheet_name=spreadsheet_name, add_timestamp=False)
    else:
        print("❌ No stock info fetched")

    # Save technical data
    if technical_results:
        df_technical = pd.DataFrame(technical_results)
        save_to_google_sheet(df_technical, worksheet_name=worksheet_name[0], creds_path=creds_path, spreadsheet_name=spreadsheet_name)
    else:
        print("❌ No successful technical analyses")

    # Save financial data
    if financial_results:
        df_financial = pd.DataFrame(financial_results)
        save_to_google_sheet(df_financial, worksheet_name=worksheet_name[1], creds_path=creds_path, spreadsheet_name=spreadsheet_name)
    else:
        print("❌ No financial data fetched")

    # Save candlestick patterns
    if patterns_results:
        combined_df = pd.concat([df for df in patterns_results if not df.empty])
        pattern_columns = [
            'Doji', 'Hammer', 'Inverted_Hammer', 'Dragonfly_Doji', 'Spinning_Top',
            'Hanging_Man', 'Shooting_Star', 'Gravestone_Doji', 'Marubozu',
            'Bullish_Kicker', 'Bullish_Engulfing', 'Bullish_Harami', 'Piercing_Line',
            'Tweezer_Bottom', 'Bearish_Kicker', 'Bearish_Engulfing', 'Bearish_Harami',
            'Dark_Cloud_Cover', 'Tweezer_Top', 'Morning_Star', 'Morning_Doji_Star',
            'Bullish_Abandoned_Baby', 'Three_White_Soldiers', 'Three_Line_Strike_Bullish',
            'Three_Inside_Up', 'Three_Outside_Up', 'Evening_Star', 'Evening_Doji_Star',
            'Bearish_Abandoned_Baby', 'Three_Black_Crows', 'Three_Line_Strike_Bearish',
            'Three_Inside_Down', 'Three_Outside_Down'
        ]
        combined_df = combined_df[combined_df[pattern_columns].any(axis=1)]
        combined_df[pattern_columns] = combined_df[pattern_columns].map(lambda x: x if x else '-')
        result_df = combined_df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close'] + pattern_columns]
        # print(f"\nCandlestick Patterns for Latest Date:")
        # print(result_df)
        save_to_google_sheet(result_df, worksheet_name=worksheet_name[2], creds_path=creds_path, spreadsheet_name=spreadsheet_name, add_timestamp=False)
    else:
        print("No patterns detected. Check data availability or adjust pattern thresholds.")

    # Save failed stocks
    if failed_stocks:
        df_failed = pd.DataFrame(failed_stocks)
        save_to_google_sheet(df_failed, worksheet_name="Error", creds_path=creds_path, spreadsheet_name=spreadsheet_name, add_timestamp=False)
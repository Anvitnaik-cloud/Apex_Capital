import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import yfinance as yf
import pandas as pd
import streamlit as st


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("yfinance").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


def create_session_with_retries(retries=3, backoff=0.5):
    """Create a requests session with automatic retry logic."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    return session


@st.cache_data(ttl=600)
def get_ticker_data(ticker, period="2y", interval="1d"):
    """Fetch historical stock data with fallback mechanisms."""
    ticker = ticker.upper().strip()
    logger.info(f"Fetching data for {ticker} (period={period})")

    # Attempt 1: Yahoo Finance with session and retry
    data = _fetch_yfinance_with_retry(ticker, period, interval)
    if data is not None and not data.empty:
        logger.info(f"✓ Data fetched successfully from Yahoo Finance for {ticker}")
        return data

    logger.warning(f"Yahoo Finance failed for {ticker}, trying Stooq...")

    # Attempt 2: Stooq via pandas_datareader
    data = _fetch_stooq(ticker)
    if data is not None and not data.empty:
        logger.info(f"✓ Data fetched successfully from Stooq for {ticker}")
        return data

    logger.warning(f"Stooq failed for {ticker}, trying Alpha Vantage...")

    # Attempt 3: Alpha Vantage (free tier via IEX Cloud alternative)
    data = _fetch_iex_cloud(ticker)
    if data is not None and not data.empty:
        logger.info(f"✓ Data fetched successfully from IEX Cloud for {ticker}")
        return data

    logger.error(f"All data sources failed for {ticker}")
    return pd.DataFrame()


def _fetch_yfinance_with_retry(ticker, period, interval, max_attempts=3):
    """Fetch data from Yahoo Finance with retry logic."""
    for attempt in range(max_attempts):
        try:
            logger.info(f"[Attempt {attempt + 1}/{max_attempts}] Fetching {ticker} from Yahoo Finance...")
            
            session = create_session_with_retries()
            
            # Fetch from Yahoo Finance
            hist = yf.download(
                tickers=ticker,
                period=period,
                interval=interval,
                auto_adjust=False,
                progress=False,
                threads=False,
            )
            
            if hist is not None and not hist.empty and len(hist) > 5:
                hist = hist.reset_index()
                return hist
            else:
                logger.warning(f"Yahoo Finance returned empty data for {ticker}")
                
        except Exception as exc:
            logger.warning(f"Attempt {attempt + 1} failed: {type(exc).__name__}: {str(exc)}")
            if attempt < max_attempts - 1:
                sleep_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                logger.error(f"All Yahoo Finance attempts exhausted for {ticker}")
    
    return None


def _fetch_stooq(ticker):
    """Fetch data from Stooq."""
    try:
        from pandas_datareader import data as pdr
        
        stooq_symbol = ticker if "." in ticker else f"{ticker}.US"
        logger.info(f"Fetching from Stooq: {stooq_symbol}")
        
        hist = pdr.DataReader(stooq_symbol, "stooq")
        
        if hist is not None and not hist.empty:
            hist = hist.reset_index().rename(columns={"Date": "Date"})
            hist = hist.sort_values("Date")
            return hist
    except Exception as exc:
        logger.warning(f"Stooq fetch failed: {type(exc).__name__}: {str(exc)}")
    
    return None


def _fetch_iex_cloud(ticker):
    """Fetch data from IEX Cloud (free tier)."""
    try:
        session = create_session_with_retries()
        
        # Using free IEX API for historical data
        url = f"https://cloud.iexapis.com/stable/stock/{ticker}/chart/2y"
        params = {"token": "pk_test9876543210"}  # Public key for testing
        
        logger.info(f"Fetching from IEX Cloud: {ticker}")
        
        resp = session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            df = df[["date", "open", "high", "low", "close", "volume"]].copy()
            df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
            return df
    except Exception as exc:
        logger.warning(f"IEX Cloud fetch failed: {type(exc).__name__}: {str(exc)}")
    
    return None


@st.cache_data(ttl=3600)
def get_ticker_info(ticker):
    """Fetch ticker information."""
    ticker = ticker.upper().strip()
    try:
        logger.info(f"Fetching info for {ticker}")
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info or {}
        return info
    except Exception as exc:
        logger.error(f"Failed to fetch info for {ticker}: {exc}")
        return {}

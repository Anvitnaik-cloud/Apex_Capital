import logging
import time
import yfinance as yf
import pandas as pd
import streamlit as st


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("yfinance").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


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

    logger.error(f"All data sources failed for {ticker}")
    return pd.DataFrame()


def _fetch_yfinance_with_retry(ticker, period, interval, max_attempts=3):
    """Fetch data from Yahoo Finance with retry logic."""
    for attempt in range(max_attempts):
        try:
            logger.info(f"[Attempt {attempt + 1}/{max_attempts}] Fetching {ticker} from Yahoo Finance...")
            # Ticker.history is more reliable than yf.download for rate limiting
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period=period, interval=interval)

            if hist is not None and not hist.empty and len(hist) > 5:
                hist = hist.reset_index()
                return hist
            logger.warning(f"Yahoo Finance returned empty data for {ticker}")
        except Exception as exc:
            logger.warning(f"Attempt {attempt + 1} failed: {type(exc).__name__}: {str(exc)}")
        if attempt < max_attempts - 1:
            logger.info("Retrying in 2s...")
            time.sleep(2)
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

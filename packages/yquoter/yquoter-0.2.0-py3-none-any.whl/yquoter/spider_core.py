# yquoter/spider_core.py
# Copyright 2025 Yodeesy
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

import time
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import Callable, Dict, List
from yquoter.logger import get_logger

logger = get_logger(__name__)

def crawl_kline_segments(
    start_date: str,
    end_date: str,
    make_url: Callable[[str, str], str],
    parse_kline: Callable[[Dict], List[List[str]]],
    sleep_seconds: float = 1.03,
    segment_days: int = 365,
) -> pd.DataFrame:
    """
    Generic paginated K-line data crawler, for scenarios where URLs are built by time segments.

        Args:
            start_date: Start date (format: "YYYYMMDD")
            end_date: End date (format: "YYYYMMDD")
            make_url: Function that takes two date strings (beg, end) and returns a constructed request URL
            parse_kline: Function that takes API response JSON data and returns a 2D list of K-line data (in string format)
            sleep_seconds: Interval between each segment request (to avoid anti-crawling), default 1 second
            segment_days: Number of days per request time segment, default 1 year (365 days)

        Returns:
            Standard K-line DataFrame with columns: date, open, high, low, close, volume, amount, change%, turnover%, change, amplitude%
    """
    # Convert input date strings to datetime objects
    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")
    current_dt = start_dt
    all_data = []

    # Set request headers to avoid being identified as a crawler
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://quote.eastmoney.com/",
    }

    # Loop to fetch data segment by segment
    while current_dt <= end_dt:
        # Calculate end date for current segment (not exceeding overall end date)
        seg_end = min(current_dt + timedelta(days=segment_days), end_dt)
        beg_str = current_dt.strftime('%Y%m%d')
        end_str = seg_end.strftime('%Y%m%d')

        # Build request URL
        url = make_url(beg_str, end_str)
        try:
            # Send request
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()  # Raise exception for HTTP status code errors
            data = resp.json()       # Parse JSON response body

            # Parse data
            rows = parse_kline(data)
            if rows:
                all_data.extend(rows)
                logger.info(f"Successfully fetched data: {beg_str} to {end_str}, total {len(rows)} rows")
            else:
                logger.info(f"No data found for segment {beg_str} to {end_str}")
        except Exception as e:
            logger.error(f"Request error: {e}")

        # Move time window to next segment
        current_dt = seg_end + timedelta(days=1)
        # Wait to prevent IP blocking
        time.sleep(sleep_seconds)

    if not all_data:
        logger.warning("K-line crawl completed with no data")
        return pd.DataFrame()

    # Build DataFrame and convert numeric columns to float type
    df = pd.DataFrame(all_data, columns=["date", "open", "high", "low", "close", "vol", "amount", "change%", "turnover%", "change", "amplitude%"])
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")  # 转换失败时设为 NaN
    logger.info(f"K-line crawl completed. Total records: {len(all_data)}")
    return df

from yquoter.config import EASTMONEY_REALTIME_MAPPING
def crawl_realtime_data(
    make_url: Callable,
    parse_realtime_data: Callable[[Dict], List[List[str]]],
    url_fields: List[str],
    user_fields: List[str],
) -> pd.DataFrame:
    """
    Crawler for real-time stock data

        Args:
            make_url: Function that returns a constructed real-time data request URL
            parse_realtime_data: Function that takes API response JSON data and returns a 2D list of real-time data
            url_fields: List of column names from the API response (to map raw data to DataFrame)
            user_fields: List of final column names required by the user (to filter and reorder DataFrame)
            column_map: Dictionary for column name mapping (key: user column name, value: API response column name)

        Returns:
            Real-time data DataFrame with user-specified columns
    """
    result = []
    logger.info("Starting real-time data crawl")
    # Set request headers to avoid being identified as a crawler
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://emweb.securities.eastmoney.com/",
    }
    # Build request URL
    url = make_url()

    try:
        # Send request
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()  # Raise exception for HTTP status code errors
        data = resp.json()  # Parse JSON response body
        # Parse real-time data
        result = parse_realtime_data(data)
        if result:
            logger.info(f"Fetched {len(result)} records of real-time data")
        else:
            logger.warning("No real-time data available")
    except Exception as e:
        logger.error(f"Error fetching real-time data: {e}")
    if not result:
        logger.warning("Real-time data crawl completed with no data")
        return pd.DataFrame()

    # Build DataFrame and map columns to user-specified names
    df = pd.DataFrame(result,columns=url_fields)
    df.rename(columns=EASTMONEY_REALTIME_MAPPING, inplace=True)
    df = df[user_fields]
    logger.info("Real-time data crawl completed successfully")
    return df


def _get_request_headers(datasource: str) -> Dict[str, str]:
    """Dynamically set headers based on the data source."""

    # Standard fallback headers
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    if datasource.lower() == 'eastmoney':
        # Specific headers for Eastmoney to mimic browser access
        base_headers["Referer"] = "https://quote.eastmoney.com/"
    elif datasource.lower() == 'xueqiu':
        # Specific headers for Xueqiu
        base_headers["Referer"] = "https://xueqiu.com/"
        # Note: Xueqiu often requires cookies. For a robust solution,
        # you might need to handle session/cookie management here.
    elif datasource.lower() == 'sina':
        # Specific headers for Sina
        base_headers["Referer"] = "https://finance.sina.com.cn/"

    return base_headers


def crawl_structured_data(
        make_url: Callable[[], str],
        parse_data: Callable[[Dict], List[List]],
        final_columns: List[str],
        datasource: str,
        sleep_seconds: float = 0.5,
) -> pd.DataFrame:
    """
    Generic crawler for fetching non-time-series, structured data (e.g., Financials, Profile, Factors).

        Args:
            make_url: Function that returns the constructed request URL.
            parse_data: Function that takes API response JSON data and returns a 2D list of data.
            final_columns: List of column names for the final DataFrame.
            datasource: The source name (e.g., 'eastmoney', 'xueqiu') used to set appropriate headers.
            sleep_seconds: Interval before the request (to avoid anti-crawling).

        Returns:
            DataFrame containing the structured data.
    """
    all_data = []

    # Dynamically set request headers based on the datasource
    headers = _get_request_headers(datasource)

    # Introduce a small delay before fetching, mirroring other functions
    time.sleep(sleep_seconds)

    # Build request URL
    url = make_url()
    logger.info(f"Starting structured data crawl from {datasource} URL: {url[:80]}...")

    try:
        # Send request
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()  # Raise exception for HTTP status code errors
        data = resp.json()  # Parse JSON response body
        # ... (rest of the try block remains the same)

        df = pd.DataFrame(data,columns=final_columns)
        # Parse data
        rows = parse_data(data)

        if rows:

            all_data.extend(rows)

            logger.info(f"Successfully fetched structured data, total {len(rows)} row(s)")
        else:
            logger.warning("No structured data found in the response")

    except requests.exceptions.HTTPError as e:
        # Ensure we check if resp is defined before accessing status_code
        status_code = resp.status_code if 'resp' in locals() else 'N/A'
        logger.error(f"HTTP Error {status_code} from {datasource}: {e}")
    except Exception as e:
        logger.error(f"Request/Parsing error for structured data from {datasource}: {e}")

    if not all_data:
        logger.warning(f"Structured data crawl from {datasource} completed with no data")
        return pd.DataFrame(columns=final_columns)

    # Build DataFrame
    df = pd.DataFrame(all_data, columns=final_columns)

    # Attempt to convert relevant columns to numeric type (e.g., for financials/factors)
    for col in df.columns:
        if 'DATE' not in col.upper() and 'CODE' not in col.upper() and 'NAME' not in col.upper() and 'INDUSTRY' not in col.upper() and 'MAIN_BUSINESS' not in col.upper():
            df[col] = pd.to_numeric(df[col], errors="coerce")

    logger.info(f"Structured data crawl from {datasource} completed. Total records: {len(all_data)}")
    return df
import yfinance as yf

from typing import Dict


def build_company(ticker: str) -> Dict[str, str]:
    tag2attribute = dict()
    try:
        ticker = yf.Ticker(ticker)
    except Exception as e:
        return tag2attribute

    info = ticker.info
    news = ticker.news

    return tag2attribute

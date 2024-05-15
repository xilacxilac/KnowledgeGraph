import ast
import pandas as pd
import yfinance as yf


def convert_string_to_list(string_list):
    try:
        return ast.literal_eval(string_list)
    except Exception:
        return []


yf_company_attr = {"industryKey",
                   "sectorKey",
                   "longBusinessSummary",
                   "fullTimeEmployees",
                   "auditRisk",
                   "boardRisk",
                   "compensationRisk",
                   "shareHolderRightsRisk",
                   "overallRisk",
                   "symbol"}
yf_company_twoway_attr = {"industryKey",
                          "sectorKey"}
location_key = {"address1", "city", "state", "country"}
labeled_events = pd.read_csv("labeled_events.csv")
labeled_events['Response'] = labeled_events['Response'].apply(convert_string_to_list)
labeled_events['Event Type NLP'] = labeled_events['Event Type NLP'].apply(convert_string_to_list)


def build_company(ticker: str) -> tuple[list[tuple[str, str]], str, tuple[str, str, str, str]]:
    tag2attribute: list[tuple[str, str]] = list()
    company: str = ""
    hq_location: tuple[str, str, str, str] = ("", "", "", "")
    try:
        ticker = yf.Ticker(ticker)
    except Exception as e:
        print(e)
        return tag2attribute, company, hq_location

    for relation, attribute in ticker.info.items():
        if relation in yf_company_attr:
            tag2attribute.append((relation, attribute))
        if relation == "shortName":
            company = attribute

    if all(loc in ticker.info and ticker.info[loc] for loc in location_key):
        hq_location = (ticker.info["address1"], ticker.info["city"], ticker.info["state"], ticker.info["country"])

    return tag2attribute, company, hq_location


def get_company_name(ticker: str) -> str:
    try:
        ticker = yf.Ticker(ticker)
    except Exception as e:
        print(e)
        return ""

    return ticker.info["shortName"]


def build_risk_factor(ticker: str) -> dict[str, tuple[list[str], list[tuple[str, str]]]]:
    year_to_events = dict()

    ticker_events = labeled_events[labeled_events["Ticker"] == ticker]
    for index, row in ticker_events.iterrows():
        dates = row["Date"].split("-")
        arr = []
        for i in range(len(row["Response"])):
            arr.append((row["Response"][i], row["Event Type NLP"][i]))

        year_to_events[dates[0]] = (dates, arr)

    return year_to_events

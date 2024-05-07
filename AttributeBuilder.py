import yfinance as yf

#from typing import Optional

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
# companyOfficers --> (maxAge, name, age, title, yearBorn, fiscalYear, totalPay, exercisedValue, unexercisedValue)
#
# maybe other financial data??


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

    #news = ticker.news

    return tag2attribute, company, hq_location


def build_risk_factor(risk_factor: str) -> list[tuple[str, str, str]]:
    pass

def build_general_event(general_event: str) -> list[tuple[str, str, str]]:
    pass

def build_event(event: str) -> list[tuple[str, str, str]]:
    pass

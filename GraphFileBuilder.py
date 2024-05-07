import yfinance as yf

msft = yf.Ticker("MSFT")

# companyOfficers --> Array(Dict(maxAge, name, age, title, yearBorn, fiscalYear, totalPay, exerciseValue, unercisedValue))
arr = []

for k, v in msft.info.items():
    print(k, v)
    #arr.append(k)

for news in msft.news:
    print(news)

#print(arr)

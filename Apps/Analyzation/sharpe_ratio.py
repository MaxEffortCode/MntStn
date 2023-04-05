


#TODO Redo this whole ratio so its simple

""" import pandas_datareader.data as web
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi

api = tradeapi.REST(
        'PKQJSU27J89VZJE92N1J',
        'zex4T98XNcnj4UoVSCPbmVAelkvvAhuboSFeAZQN',
        'https://paper-api.alpaca.markets', api_version='v2'
)


#takes space seperated list of tickerspd.DataFrame
#tickers = [str(ticker) for ticker in input("List Elements Seperated By Spaces:").split()]
tickers = ["msft","tsla","googl","fb","aapl"]

plt.style.use('ggplot')
#2020-10-01 00:00:00
end = dt.date.today()
end.strftime("%Y-%m-%d")
day_delta = dt.timedelta(days=4)
end= end - day_delta
print(end)
year_back = dt.timedelta(days=5)
start = end - year_back





#lister = api.get_bars(tickers[0], tradeapi.rest.TimeFrame.Minute, start, end, adjustment='raw').df
#lister = lister["volume"]
lister = pd.DataFrame()

for ticker in tickers:
    mt = api.get_bars(ticker, tradeapi.rest.TimeFrame.Minute, start, end, adjustment='raw').df
    ticker_df = mt["volume"]
    lister[f'{ticker}'] = ticker_df
    ticker_df.to_frame()
    print(ticker_df)
    #gca auto generates axises

    ticker_df.plot(kind='line', color=np.random.rand(3,), label=f'{ticker}')
    

plt.show()

mt['test'] = ticker_df.values
lister.to_csv(path_or_buf="renn.csv")


print(lister)
print("herereereerre\n\n\n\n\n")
print(ticker_df)

#mt.to_csv(path_or_buf="renn.csv")
mt = mt.pct_change().dropna()
mt['Port'] = mt.mean(axis=1)
(mt+1).cumprod()[-1:]
mt.plot()
plt.show()


def sharpe_ratio(return_series, N, rf):
    mean = return_series.mean() * N -rf
    sigma = return_series.std() * np.sqrt(N)
    return mean / sigma

#tickers = ['AAPL', 'AMZN', 'MSFT', 'GOOGL','FB']
#grabs data from yahoo finance
stocks = web.DataReader(tickers,
                        'yahoo', start, end)['Adj Close']
print(stocks)
df = stocks.pct_change().dropna()
df['Port'] = df.mean(axis=1) # 20% apple, ... , 20% facebook
(df+1).cumprod()[-1:]


N = 255 #255 trading days in a year
rf =0.01 #1% risk free rate
sharpes = df.apply(sharpe_ratio, args=(N,rf,),axis=0)
print(sharpes)

sharpes.plot()
plt.show()





#stock price
#print(stocks.head())

#changes stock to percentage by taking the 1-[(day_current-1)/(day_current)]
#df = stocks.pct_change().dropna()

#takes the collection in the stock array and calculates: sum(tickers_percent_change)/(num of tickers) AKA mean 
#df['Port'] = df.mean(axis=1) # 20% apple, ... , 20% facebook

#displaces percentage of daily change of each stock and their daily mean
#print(df.head())

#takes percentage change and adds it to 1
#(ticker_percent_change_daily)+1
#literally just adds one to every value
#print((df+1).head())

#multiplies up each value in the array columns iteratively
#ie cummulitive_product[1 2 3 4] = [(1), (1*2), (1*2*3), (1*2*3*4)] = [1, 2, 6, 24]
#print((df+1).cumprod().head())

#shows how each stock imporved through a normalized percentage
#alogn with showing the mean normalized average
#(df+1).cumprod().plot()
#plt.show()

#grabs the final row in the cumprod array
# (df+1).cumprod()[-1:]



# N = 255 #255 trading days in a year
# rf =0.01 #1% risk free rate
# sharpes = df.apply(sharpe_ratio, args=(N,rf,),axis=0)
# print(sharpes)
"""
#sharpes.plot.bar()
#plt.show()



#back_test(date_begin= something, date_end = something, chart_against = <volume, price, bids, bid spead, ect..> , chart_to_test = <my_hpothesis> ) """
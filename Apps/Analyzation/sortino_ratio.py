


#TODO Redo this whole ratio so its simple




""" import pandas_datareader.data as web
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('ggplot')


start = dt.datetime(2013, 1, 1)
end = dt.datetime(2020, 10, 1)

#takes space seperated list of tickers
tickers = [str(ticker) for ticker in input("List Elements Seperated By Spaces:").split()]

#tickers = ['AAPL', 'AMZN', 'MSFT', 'GOOGL','FB']
#grabs data from yahoo finance
stocks = web.DataReader(tickers,
                        'yahoo', start, end)['Adj Close']




#stock price
print(stocks.head())

#changes stock to percentage by taking the 1-[(day_current-1)/(day_current)]
df = stocks.pct_change().dropna()

#takes the collection in the stock array and calculates: sum(tickers_percent_change)/(num of tickers) AKA mean 
df['Port'] = df.mean(axis=1) # 20% apple, ... , 20% facebook

#displaces percentage of daily change of each stock and their daily mean
print(df.head())

#takes percentage change and adds it to 1
#(ticker_percent_change_daily)+1
#literally just adds one to every value
print((df+1).head())

#multiplies up each value in the array columns iteratively
#ie cummulitive_product[1 2 3 4] = [(1), (1*2), (1*2*3), (1*2*3*4)] = [1, 2, 6, 24]
print((df+1).cumprod().head())

#shows how each stock imporved through a normalized percentage
#alogn with showing the mean normalized average
(df+1).cumprod().plot()
plt.show()

#grabs the final row in the cumprod array
(df+1).cumprod()[-1:]

def sharpe_ratio(return_series, N, rf):
    mean = return_series.mean() * N -rf
    sigma = return_series.std() * np.sqrt(N)
    return mean / sigma

N = 255 #255 trading days in a year
rf =0.01 #1% risk free rate
sharpes = df.apply(sharpe_ratio, args=(N,rf,),axis=0)

sharpes.plot.bar()
plt.show() """
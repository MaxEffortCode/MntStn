import alpaca_trade_api as tradeapi

#api key PKQJSU27J89VZJE92N1J
#secret key: ask in discord


#TODO make env variables to hold secrets
api = tradeapi.REST(
        '<api_key>',
        '<secret_key>',
        'https://paper-api.alpaca.markets', api_version='v2'
)
        
#Example: Submit a market order to buy 1 share of Apple at market price
""" api.submit_order(
    symbol='AAPL',
    qty=1,
    side='buy',
    type='market',
    time_in_force='gtc'
) """
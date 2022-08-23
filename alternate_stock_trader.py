'''
Created on Jul 12, 2022

@author: Hamza Kashubeck

  This trader takes a different approach that is significantly less reliant on technical indicators. It chooses an entry position based on an indicator
  (currently the stochastic rsi) and closes the position after reaching a desired profit amount.

  From my testing so far, this trader seems to be more profitable than _stock_trader.py. This may be because (as of my testing period) the market is 
  trending upward. 
  
'''

import talib
import alpaca_trade_api as api
from yahooquery import Ticker
import time
from datetime import datetime

# TO DO NEXT:
#
#     1. NEW IDEA: make a trader that holds the SPY as a baseline.
#     Every now and then (maybe based on indicators, maybe not) it sells and rebuys at a lower price.
#     Maybe that way it will be possible to actually beat the s&p? idk tho

# MAKE ORDERS GOOD UNTIL CANCELLED, NOT DAY ORDERS
    


# ---------------- ALPACA HELPER FUNCTIONS HERE -------------------- #

    # submits a market buy order. returns the resulting Alpaca order object
def market_buy(ticker,qty):
    return alpaca.submit_order(ticker.upper(), qty, side='buy', type='market')
    
    # submits a market sell order. returns the resulting Alpaca order object
def market_sell(ticker,qty):
    return alpaca.submit_order(ticker.upper(), qty, side='sell', type='market')
    
    # submits a limit buy order. returns the resulting Alpaca order object
def limit_buy(ticker,qty,limit):
    return alpaca.submit_order(ticker.upper(), qty, side='buy', type='limit', limit_price=limit)
    
    # submits a limit sell order. returns the resulting Alpaca order object
def limit_sell(ticker,qty,limit):
    return alpaca.submit_order(ticker.upper(), qty, side='sell', type='limit', limit_price=limit)
    
    # submits a trailing stop sell order for a given percent. returns the resulting order object
def trailing_stop_percent(ticker,qty,percent):
    return alpaca.submit_order(ticker.upper(), qty, side='sell', type='trailing_stop', trail_percent=percent)

    #retrieves the order status of a given order
    #Possible statuses: new, filled OR partially_filled, cancelled, expired, and other less common statuses
def order_status(order_id):
    #to get an order_id, syntax is orderObj.id
    order = alpaca.get_order(order_id)
    return order.status
    
# ---------------- STOCK RESEARCH HELPER FUNCTIONS HERE -------------------- #

    #retrieves the current market price from yahoo finance
def get_price(ticker):
    return round(Ticker(ticker).price[ticker]['regularMarketPrice'],2)

    #retrieves the current bid price from yahoo finance
def get_bid_price(ticker):
    return Ticker(ticker).summary_detail[ticker]['bid']

    #retrieves the current ask price from yahoo finance
def get_ask_price(ticker):
    return Ticker(ticker).summary_detail[ticker]['ask']

    #retrieves stochastic rsi values calculated from recent minute closing prices from yahoo finance
def get_stochrsi(ticker):
    candles = Ticker(ticker).history(period='3d', interval='1m')
    return talib.stream_STOCHRSI(candles.close, fastk_period=5)


# --------------------- ALGORITHM SIGNAL FUNCTIONS --------------------------- #

    # returns a 0 for inconclusive, 1 for buy signal, 2 for sell signal
def get_stochrsi_signal(ticker):
    k, d = get_stochrsi(ticker)
    
    print(k)
    if k < 20:
        # wait until the stochastic rsi fast k line rebounds above the oversold mark
        
#         is this the best way to solve this problem? this will need to be changed before 
#         it's possible to use multiple indicators simultaneously
        
        print("entered stochrsi buy signal loop:")
        while k<20:
            #do nothing
            time.sleep(1)
            k, d = get_stochrsi(ticker)
            print(k)
        #at this point, the fast k line is rebounding above the 20 mark.
        print('STOCHRSI BUY signal at '+str(datetime.now()))
        return 1
    if k > 80:
        # sell immediately when the fast k line hits 80
        print('STOCHRSI SELL signal at '+str(datetime.now()))
        return 2
    
# --------------------- TESTING/SIMULATION FUNCTIONS --------------------------- #
    
    #runs the main simulation. parameter is the desired algorithm signal function to be used for buy/sell signals.
def trade_SPY(signal_func):
    ticker = 'SPY'
    
    last_signal = 0
    while(True):
        
        try:
            time.sleep(1)
            signal = signal_func(ticker)
        except Exception as e:
            print(e)
            time.sleep(5)
            signal = 0
        
        if signal == 1: #BUY
            if last_signal!=1: #only buy once per signal
                last_signal = 1
                try:
                    limit_price = float(get_ask_price(ticker))+0.15
                    buy_order = limit_buy(ticker,1,round(limit_price,2)) #Buy around the current ask price
                    print('BUY ORDER AT '+str(datetime.now()))
                    time.sleep(10) # give it a few seconds to execute the buy order (or not execute it)
                    bought_price = alpaca.get_order(buy_order.id).filled_avg_price
                    limit_sell(ticker,1,round(float(bought_price)+0.1,2))
                    print('SELL ORDER SUBMITTED FOR'+str(bought_price))
                except Exception as e:
                    print(e)
                    #order will fail if not enough cash available, or if something is up with the order
                    # handle differently: if e is due to buying power vs. the limit sell failing because the buy didn't execute
                
                """  elif signal == 2: #SELL
            if last_signal!=2: #only sell once per signal
                last_signal = 2
                #qty_held = int(alpaca.get_position(ticker).qty)
                try:
                    limit_sell(ticker,1,round(get_bid_price(ticker)-0.25,2)) #Sell around the current bid price
                    print('SELL ORDER AT '+str(datetime.now()))
                except Exception as e:
                    print(e)
                    print('SELL ORDER AT '+str(datetime.now())+ ', but no shares are currently owned.')
                    """
        else:
            #print('no signal to report')
            last_signal = 0
            
        # loop through and cancel all unfulfilled buy orders
        orders = alpaca.list_orders(side='buy')
        for order in orders:
            alpaca.cancel_order(order.id)
            print(order)
            
            
            

# ----------------------- END HELPER FUNCTIONS ----------------------------- #

# The following input values would be specific to my Alpaca account:
API_KEY = ''
API_SECRET = ''
BASE_URL = 'https://paper-api.alpaca.markets'

alpaca = api.REST(API_KEY, API_SECRET, BASE_URL)

#modify the following statement to run different technical indicators
signal_func = get_stochrsi_signal

trade_SPY(signal_func)

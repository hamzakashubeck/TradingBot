'''
Created on Jul 12, 2022

@author: Hamza Kashubeck

  This trader takes a different approach that is significantly less reliant on technical indicators. It chooses an entry position based on an indicator
  (currently the stochastic rsi) and closes the position after reaching a desired profit amount. 
  It also used the same strategy to strengthen existing positions by attempting to buy stocks in the current portfolio at a lower price.

  From my testing so far, this trader seems to be more profitable than _stock_trader.py.
  
'''

# NEXT STEPS:
#    Fix indicator calculation or candle scraping. 
#        Need stochastic momentum index. This indicator or historical query is giving bad info/signals.

import talib
import alpaca_trade_api as api
from yahooquery import Ticker
import time
from datetime import datetime
    


# ---------------- ALPACA HELPER FUNCTIONS HERE -------------------- #

    # submits a market buy order. returns the resulting Alpaca order object
def market_buy(ticker,qty):
    return alpaca.submit_order(ticker.upper(), qty, side='buy', type='market')
    
    # submits a market sell order. returns the resulting Alpaca order object
def market_sell(ticker,qty):
    return alpaca.submit_order(ticker.upper(), qty, side='sell', type='market')
    
    # submits a limit buy order. returns the resulting Alpaca order object
def limit_buy(ticker,qty,limit):
    return alpaca.submit_order(ticker.upper(), qty, side='buy', type='limit', time_in_force = 'gtc', limit_price=limit)
    
    # submits a limit sell order. returns the resulting Alpaca order object
def limit_sell(ticker,qty,limit):
    return alpaca.submit_order(ticker.upper(), qty, side='sell', type='limit', time_in_force = 'gtc', limit_price=limit)
    
# submits a fill or kill buy order. returns the resulting Alpaca order object
def fok_buy(ticker,qty,limit):
    return alpaca.submit_order(ticker.upper(), qty, side='buy', type='limit', time_in_force = 'fok', limit_price=limit)
    
    # submits a fill or kill sell order. returns the resulting Alpaca order object
def fok_sell(ticker,qty,limit):
    return alpaca.submit_order(ticker.upper(), qty, side='sell', type='limit', time_in_force = 'fok', limit_price=limit)
    
    
    # submits a trailing stop sell order for a given percent. returns the resulting order object
def trailing_stop_percent(ticker,qty,percent):
    return alpaca.submit_order(ticker.upper(), qty, side='sell', type='trailing_stop', trail_percent=percent)

    #retrieves the order status of a given order
    #Possible statuses: new, filled OR partially_filled, cancelled, expired, and other less common statuses
def order_status(order_id):
    #to get an order_id, syntax is orderObj.id
    order = alpaca.get_order(order_id)
    return order.status

def kill_orders(order_side):
    # loop through and cancel all unfulfilled buy orders
    orders = alpaca.list_orders(side=order_side)
    for order in orders:
        alpaca.cancel_order(order.id)
        print(order)
    
    
# ---------------- STOCK RESEARCH HELPER FUNCTIONS HERE -------------------- #

    #retrieves the current market price from yahoo finance
def get_price(ticker):
    return alpaca.get_latest_trade('SPY').p

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
        
        print("entered stochrsi buy signal loop:")
        while k<5:
            #do nothing
            time.sleep(1)
            k, d = get_stochrsi(ticker)
            print(k)
        #at this point, the fast k line is passing above the 20 mark.
        print('STOCHRSI BUY signal at '+str(datetime.now()))
        return 1
    
    elif k > 80:
        # wait until the stochastic rsi fast k line falls below the undersold mark
        
        print("entered stochrsi sell signal loop:")
        while k>95:
            #do nothing
            time.sleep(1)
            k, d = get_stochrsi(ticker)
            print(k)
        #at this point, the fast k line is falling below the 80 mark.
        print('STOCHRSI SELL signal at '+str(datetime.now()))
        return 2
    
    return 0
    
# --------------------- TESTING/SIMULATION FUNCTIONS --------------------------- #
    
    #runs the main simulation. parameter is the desired algorithm signal function to be used for buy/sell signals.
def trade_SPY(signal_func):
    ticker = 'SPY'
    
    #have some shares on hand to start
    market_buy('SPY',100);
    
    while(True):
        
        try:
            time.sleep(1)
            signal = signal_func(ticker)
        except Exception as e:
            print(e)
            time.sleep(5)
            signal = 0
        
        if signal == 1: #BUY
            try:
                limit_price = float(get_price(ticker))+0.15
                buy_order = fok_buy(ticker,1,round(limit_price,2)) #Buy around the current ask price
                print('BUY ORDER AT '+str(datetime.now()))
                
                time.sleep(3)
                
                bought_price = alpaca.get_order(buy_order.id).filled_avg_price
                limit_sell(ticker,1,round(float(bought_price)+0.1,2))
                print('SELL ORDER SUBMITTED FOR'+str(float(bought_price)+0.1))
            except Exception as e:
                print(e)
                #order will fail if not enough cash available, or if something is up with the order
                # handle differently: if e is due to buying power vs. the limit sell failing because the buy didn't execute
    
        elif signal == 2: #SELL
            try:
                limit_price = float(get_price(ticker))-0.15
                sell_order = fok_sell(ticker,1,round(limit_price,2)) #Buy around the current ask price
                print('SELL ORDER AT '+str(datetime.now()))
 
                time.sleep(3)
                
                sold_price = alpaca.get_order(sell_order.id).filled_avg_price
                limit_buy(ticker,1,round(float(sold_price)-0.1,2))
                print('RE-BUY ORDER SUBMITTED FOR'+str(float(sold_price)-0.1))
            except Exception as e:
                print(e)
                #order will fail if not enough cash available, or if something is up with the order
                # handle differently: if e is due to buying power vs. the limit sell failing because the buy didn't execute
        
            
            

# ----------------------- END HELPER FUNCTIONS ----------------------------- #

# The following input values would be specific to my Alpaca account:
API_KEY = ''
API_SECRET = ''
BASE_URL = 'https://paper-api.alpaca.markets'

alpaca = api.REST(API_KEY, API_SECRET, BASE_URL)

#modify the following statement to run different technical indicators
signal_func = get_stochrsi_signal

trade_SPY(signal_func)

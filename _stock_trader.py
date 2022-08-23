'''
Created on Jul 12, 2022

@author: Hamza Kashubeck
'''

import talib
import alpaca_trade_api as api
from yahooquery import Ticker
import time
from datetime import datetime

# TO DO NEXT:
#
#     1. Write a function that returns a signal based on several technical indicators at once. Possibly takes 
#        in a list of function pointers and weighs them equally?
#            One way to do this effeciently may be to modify the algorithm signal functions to take in the
#            list of historical prices, instead of having each one make a new call to the yahooquery API.
#
#     2. Been getting a lot of exceptions involving inability to communicate with yahooquery near the start
#        of the trade_SPY() function. Could just be internet connection issues, but find a solution and fix.
    


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

    #retrieves the current rsi value calculated from recent minute closing prices from yahoo finance
def get_rsi_val(ticker):
    candles = Ticker(ticker).history(period='3d', interval='1m')
    return talib.stream_RSI(candles.close,timeperiod = 12)

    #retrieves bollinger band values calculated from recent minute closing prices from yahoo finance
def get_bbands(ticker):
    candles = Ticker(ticker).history(period='3d', interval='1m')
    return talib.stream_BBANDS(candles.close)

    #retrieves stochastic rsi values calculated from recent minute closing prices from yahoo finance
def get_stochrsi(ticker):
    candles = Ticker(ticker).history(period='3d', interval='1m')
    return talib.stream_STOCHRSI(candles.close, fastk_period=5)

    #retrieves adx, di+, and di- values calculated from recent minute prices from yahoo finance
def get_adx(ticker):
    candles = Ticker(ticker).history(period='3d', interval='1m')
    adx = talib.stream_ADX(candles.high, candles.low, candles.close)
    di_plus = talib.stream_PLUS_DI(candles.high, candles.low, candles.close)
    di_minus = talib.stream_MINUS_DI(candles.high, candles.low, candles.close)
    return adx, di_plus, di_minus
    

# --------------------- ALGORITHM SIGNAL FUNCTIONS --------------------------- #

    # returns a 0 for inconclusive, 1 for buy signal, 2 for sell signal
def get_bbands_signal(ticker):
    price = get_price(ticker)
    upper, middle, lower = get_bbands(ticker)
    if price < lower:
        print('bbands BUY signal at '+str(datetime.now())+ ' at a price of '+str(price))
        return 1
    if price > upper:
        print('bbands SELL signal at '+str(datetime.now())+ ' at a price of '+str(price))
        return 2
    return 0

    # returns a 0 for inconclusive, 1 for buy signal, 2 for sell signal
def get_rsi_signal(ticker):
    rsi = get_rsi_val(ticker)
    if rsi < 30:
        print('RSI BUY signal at '+str(datetime.now()))
        return 1
    if rsi > 70:
        print('RSI SELL signal at '+str(datetime.now()))
        return 2
    return 0

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
    
    # returns a 0 for inconclusive, 1 for buy signal, 2 for sell signal
def get_adx_signal(ticker):
    # ADX above 20 and DI+ over DI- signifies an uptrend
    # ADX above 20 and DI- above DI+ signifies a downtrend
    adx, di_plus, di_minus = get_adx(ticker)
    if adx >20:
        if di_plus > di_minus:
            print('ADX UPTREND signal at '+str(datetime.now()))
            return 1
        else:
            print('ADX DOWNTREND signal at '+str(datetime.now()))
            return 2
    return 0
    
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
        
        #cancel all unresolved orders
        alpaca.cancel_all_orders()
        
        if signal == 1: #BUY
            
            # if buy signal is active, and there aren't any shares currently held
            if last_signal!=1: #only buy once per signal
                last_signal = 1
                try:
                    limit_buy(ticker,1,round(get_ask_price(ticker)+0.2,2)) #Buy around the current ask price
                    print('BUY ORDER AT '+str(datetime.now()))
                except Exception as e:
                    print(e)
                    print('BUY ORDER AT '+str(datetime.now())+ ', but not enough buying power.')
                #order will fail if not enough cash available
                
        elif signal == 2: #SELL
            
            if last_signal!=2: #only sell once per signal
                last_signal = 2
                #qty_held = int(alpaca.get_position(ticker).qty)
                try:
                    limit_sell(ticker,1,round(get_bid_price(ticker)-0.2,2)) #Sell around the current bid price
                    print('SELL ORDER AT '+str(datetime.now()))
                except Exception as e:
                    print(e)
                    print('SELL ORDER AT '+str(datetime.now())+ ', but no shares are currently owned.')
        else:
            #print('no signal to report')
            last_signal = 0

# ----------------------- END HELPER FUNCTIONS ----------------------------- #

# The following input values would be specific to my Alpaca account:
API_KEY = ''
API_SECRET = ''
BASE_URL = 'https://paper-api.alpaca.markets'

alpaca = api.REST(API_KEY, API_SECRET, BASE_URL)

#modify the following statement to run different technical indicators
signal_func = get_stochrsi_signal

trade_SPY(signal_func)

'''
Created on Jul 29, 2022

@author: hamzakashubeck
'''
import talib
import alpaca_trade_api as api
from yahooquery import Ticker
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup


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
    
# ---------------- CRYPTO RESEARCH HELPER FUNCTIONS HERE -------------------- #

    #retrieves the current midpoint price scraped from robinhood. 
    # TO-DO: find a more efficient and accurate way to grab crypto asset prices
def get_crypto_price(ticker):
    robinhood_html = requests.get('https://robinhood.com/crypto/'+ticker.upper()).text
    robinhood_soup = BeautifulSoup(robinhood_html, 'lxml')
    price_soup = robinhood_soup.find_all('span', class_ = 'css-w425uz')
    price = price_soup[1:3]+price_soup[4:10]
    final_price = ''
    for entry in price:
        final_price += entry.text
    return float(final_price)

def get_bid_price(ticker):
    #TO-DO: currently only midpoint price is available. find a way to grab bid and ask prices
    return -1

def get_ask_price(ticker):
    #TO-DO: see note above
    return -1
 
    #retrieves the current rsi value calculated from recent yahoo finance historical pricing
    # currently retrieves data in two-minute intervals, despite the function calling for one minute)
def get_rsi_val(ticker):
    candles = Ticker(ticker).history(period='5d', interval='1m')
    return talib.stream_RSI(candles.close,timeperiod = 12)

    #retrieves bollinger band values calculated from recent minute closing prices from yahoo finance
def get_bbands(ticker):
    candles = Ticker(ticker).history(period='5d', interval='1m')
    return talib.stream_BBANDS(candles.close)

# --------------------- ALGORITHM/TESTING FUNCTIONS --------------------------- #

    # returns a 0 for inconclusive, 1 for buy signal, 2 for sell signal
def get_bbands_signal(ticker):
    price = get_crypto_price('BTC')
    upper, middle, lower = get_bbands(ticker)
    if price < lower:
        print('bbands BUY signal at '+str(datetime.now())+ ' at a price of '+str(price))
        return 1
    if price > upper:
        print('bbands SELL signal at '+str(datetime.now())+ ' at a price of '+str(price))
        return 2
    return 0
  
    #runs the main simulation
def trade_BTC_bbands_test():
    alpaca_ticker = 'BTC/USD'
    pos_ticker = 'BTCUSD'
    yticker = 'BTC-USD'
    
    last_signal = 0
    while(True):
        signal = get_bbands_signal(yticker)
        if signal == 1:
            if last_signal!=1: #BUY
                last_signal = 1
                try:
                    market_buy(alpaca_ticker,1)
                    print('BUY ORDER AT '+str(datetime.now()))
                except:
                    print('BUY ORDER AT '+str(datetime.now())+ ', but not enough buying power.')
                
                #order will fail if not enough cash available
        elif signal == 2: #SELL
            last_signal = 2
            #qty_held = int(alpaca.get_position(pos_ticker).qty)
            #if qty_held>0:
            try:
                alpaca.close_position(pos_ticker)
                print('SELL ALL ORDER AT '+str(datetime.now()))
            except:
                print('SELL ALL ORDER AT '+str(datetime.now())+ ', but no shares are currently owned.')
        else:
            last_signal = 0
        
# ----------------------- END HELPER FUNCTIONS ----------------------------- #


API_KEY = ''
API_SECRET = ''
BASE_URL = 'https://paper-api.alpaca.markets'

alpaca = api.REST(API_KEY, API_SECRET, BASE_URL)

trade_BTC_bbands_test()

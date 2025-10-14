import json
import time
import requests
import hmac
import hashlib
import os
from datetime import datetime
from ta.trend import EMAIndicator, SMAIndicator
import ccxt
import pandas as pd

def PLACE_BRACKET_ORDER(api_key, api_secret, price, SL, TP, LOT, side, product_symbol, product_id, base_url ):
    if api_key is None:
        print(f"api_key is missing ")
    if 	api_secret is None:
        print(f"api_key is missing ")
    if price is None:
        print(f"Price is empty, oder is place on market price")
        price = "market_order"
    else:
        print(f"Emtry is {price}")
    if SL is None:
        print(f"STOPLOSS is not provided")
    if TP is None:
        print(f"Traget is missing")
    if LOT is None:
        print(f"LOT size is empty")
    if side is None:
        print(f"Order type (BUY/SELL) is missing")
    if product_symbol is None:
        print(f"Coin name  is missing")
    if product_id is None:
        print(f"Coin ID is missing")
    if base_url is None:
        print(f"API URL is missing")		
    #base_url = 'https://api.india.delta.exchange'  # Δ India production
    endpoint = '/v2/orders'
    url = base_url + endpoint
    method = 'POST'
    
    # === Helper to generate HMAC signature ===
    def generate_signature(secret, message):
        message = bytes(message, 'utf-8')
        secret = bytes(secret, 'utf-8')
        return hmac.new(secret, message, hashlib.sha256).hexdigest()
    
    
    timestamp = str(int(time.time()))
    # === Bracket Order Payload ===
    order = {
        "product_id": f"{product_id}",
        "product_symbol": f"{product_symbol}",
        "side": f"{side}",
        "size": f"{LOT}",
        "order_type": f"{price}",
        "time_in_force": "gtc",

        # Bracket params
        "bracket_stop_loss_price": f"{SL}",
        "bracket_stop_loss_limit_price": f"{SL}",
        "bracket_take_profit_price": f"{TP}",
        "bracket_take_profit_limit_price": f"{TP}",
        "stop_trigger_method": "last_traded_price"
    }
    query_string = ''
    # === Prepare body and signature ===
    body = json.dumps(order, separators=(',', ':'))
    signature_data = method + timestamp + endpoint + query_string + body
    #print("signature_data", signature_data)
    sig = generate_signature(api_secret,signature_data)
    headers = {
        "api-key": api_key,
        "timestamp": str(timestamp),
        "signature": sig,
        "Content-Type": "application/json"
    }
    
    # === Send the request ===
    response = requests.post(url, headers=headers, data=body)    
    confirm = response.json()
    if confirm:
        success = confirm.get("success")
        if success:
            print(f"{json.dumps(response.json(), indent=2)}")
            print(f"Order has been created sucessfully")
        else:
            print(f"Unable to place order")
            print(f"{json.dumps(response.json(), indent=2)}")
def PLACE_ORDER(api_key, api_secret, price, LOT, side, product_id, base_url ):        	
    if api_key is None:
        print(f"api_key is missing ")
    if 	api_secret is None:
        print(f"api_key is missing ")
    if price is None:
        print(f"Price is empty, oder is place on market price")
        price = "market_order"
    else:
        print(f"Emtry is {price}")
    if LOT is None:
        print(f"LOT size is empty")
    if side is None:
        print(f"Order type (BUY/SELL) is missing")
    if product_id is None:
        print(f"Coin ID is missing")
    if base_url is None:
        print(f"API URL is missing")
    endpoint = '/v2/orders'
    url = base_url + endpoint
    method = 'POST'
    def generate_signature(secret, message):
        message = bytes(message, 'utf-8')
        secret = bytes(secret, 'utf-8')
        return hmac.new(secret, message, hashlib.sha256).hexdigest()
    timestamp = str(int(time.time()))
    order = {
        "product_id": f"{product_id}",       # ETHUSD
        "size": f"{LOT}",               # contract size
        "side": f"{side}",           # 'buy' or 'sell'
        "order_type": f"{price}",  # or "limit_order"
        "time_in_force": "gtc"    # good till cancel
    }
    query_string = ''
    # === Prepare body and signature ===
    body = json.dumps(order, separators=(',', ':'))
    signature_data = method + timestamp + endpoint + query_string + body
    #print("signature_data", signature_data)
    sig = generate_signature(api_secret,signature_data)
    headers = {
        "api-key": api_key,
        "timestamp": str(timestamp),
        "signature": sig,
        "Content-Type": "application/json"
    }
    
    # === Send the request ===
    response = requests.post(url, headers=headers, data=body)

    # === Send the request ===
    response = requests.post(url, headers=headers, data=body)    
    confirm = response.json()
    if confirm:
        success = confirm.get("success")
        if success:
            print(f"{json.dumps(response.json(), indent=2)}")
            print(f"Order has been created sucessfully")
        else:
            print(f"Unable to place order")
            print(f"{json.dumps(response.json(), indent=2)}")
def BALANCE_CHECK(api_key, api_secret, base_url ):
    if api_key is None:
        print("API KEY is missing .. !!")
    if api_secret is None:
        print("api_secret is missing")
    if base_url is None:
        print("base_url is missing")
    endpoint = "/v2/wallet/balances"
    method = "GET"
    timestamp = str(int(time.time()))
    def generate_signature(secret, message):
        message = bytes(message, 'utf-8')
        secret = bytes(secret, 'utf-8')
        return hmac.new(secret, message, hashlib.sha256).hexdigest()
    signature_data = method + timestamp + endpoint
    sig = generate_signature(api_secret,signature_data)
    headers = {
        "api-key": api_key,
        "timestamp": timestamp,
        "signature": sig,
    }
    response = requests.get(base_url + endpoint, headers=headers)
    data = response.json()
    balance = data['result'][0]['available_balance_inr']
    return balance         

def CURRENT_PRICE(product_symbol):
    if product_symbol is None:
        print("Coin name is missing..")
    exchange = ccxt.binance()
    ticker = exchange.fetch_ticker(product_symbol)
    price = ticker['last']
    return price
    
def EMA(symbol, lookback, timeframe, ema_value):
    exchange = ccxt.binance()
    if symbol is None:
        print("symbol is not define ")
    if lookback is None:
        print("lookback is not define ")
    if timeframe is None:
        print("timeframe is not define")
    if ema_value is None:
        print("ema_value is not define")
  
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=lookback)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # === INDICATORS ===
    ema = EMAIndicator(close=df['close'], window=ema_value).ema_indicator()
    df['EMA'] = ema
    latest_ema = df['EMA'].iloc[-1]
    return latest_ema


def MOVING_AVG(symbol, lookback, timeframe, ma_value):
    exchange = ccxt.binance()
    if symbol is None:
        print("symbol is not define ")
    if lookback is None:
        print("lookback is not define ")
    if timeframe is None:
        print("timeframe is not define")
    if ma_value is None:
        print("ma_value is not define")

    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=lookback)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    ma = SMAIndicator(close=df['close'], window=ma_value).sma_indicator()
    df['MA'] = ma
    latest_ma = df['MA'].iloc[-1]
    return latest_ma
def EMA_MA_CROSSOVER(symbol, lookback, timeframe, ma_value, ema_value):
    exchange = ccxt.binance()
    if symbol is None:
        print("symbol is not define ")
    if lookback is None:
        print("lookback is not define ")
    if timeframe is None:
        print("timeframe is not define")
    if ma_value is None:
        print("ma_value is not define")
    if ema_value is None:
        print("ema_value is not define")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=lookback)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    ma = SMAIndicator(close=df['close'], window=ma_value).sma_indicator()
    ema = EMAIndicator(close=df['close'], window=ema_value).ema_indicator()
    df['EMA'] = ema
    df['MA'] = ma
    df['prev_EMA'] = df['EMA'].shift(1)
    df['prev_MA'] = df['MA'].shift(1)
    latest_ma = df['MA'].iloc[-1]
    latest_ema = df['EMA'].iloc[-1]
    if (df.iloc[-2]['EMA'] < df.iloc[-2]['MA']) and (df.iloc[-1]['MA'] > df.iloc[-1]['MA']):
        status = f"EMA_{ema_value} CROSSED ABOVE TO MOVING AVERAGE {ma_value}"
    elif (df.iloc[-2]['EMA'] > df.iloc[-2]['MA']) and (df.iloc[-1]['MA'] < df.iloc[-1]['MA']):
        status = f"EMA_{ema_value} CROSS BELOW TO MOVING AVERAGE {ma_value}"
    else:
        if latest_ema > latest_ma:
            market = "EMA is above MA → Bullish trend"
        elif latest_ema < latest_sma:
            market = "EMA9 is below SMA14 → Bearish trend"
        else:
            market = "EMA9 equals SMA14 → Neutral trend"            
        status = f" {symbol} -> {market},  CROSSOVER IS NOT YET"
    return status        
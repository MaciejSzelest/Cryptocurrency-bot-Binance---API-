# Import modules
import websocket, json, pprint, numpy, talib
from binance.client import Client
from binance.enums import *

# Websocket module parameters
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
TRADE_SYMBOL = "ETHUSD"
TRADE_QUANTITY = 0.005

# Ta-lib module parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Binance API keys (Crate account on binance.com, in settings you can create your own secret API keys.
API_KEY = '' # Provide key
API_SECRET = '' # Provide key

# Binance log in
client = Client(API_KEY, API_SECRET, tld='us')


closes = []
in_position = False

# Order function, triggered by RSI parameters like overbought or oversold
def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("Sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print(f"An exception occurred: {e}")
        return False
    return True


# Websocket functions, to inform about current status
def on_open(ws):
    print("Opened connection.")


def on_close(ws):
    print("Closed connection.")

# Whole process of triggering the buy/sell order based on the data from websocket about closed candle.
# Together with RSI indicator, with specific hard-coded parameters.
def on_message(ws, message):
    global closes, in_position

    print("Received message.")
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json.message["k"]
    is_candle_closed = candle["x"]
    close = candle["c"]

    if is_candle_closed:
        print(f"Candle closed at {close}")
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("All RSIs calculated so far: ")
            print(rsi)
            last_rsi = rsi[-1]
            print(f"Current RSI is: {last_rsi}")

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Sell position!")
                    # put binance sell logic here
                    order_succeeded = order.client.create_order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, however we don't own any. Nothing to do.")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, however you already own it, nothing to do.")
                print("Buy position!")
                # put binance order logic here
                order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    in_position = True

# ETH/USDT data sourcing from websocket with 1M tenor, with endless loop
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

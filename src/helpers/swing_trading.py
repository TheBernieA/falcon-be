import MetaTrader5 as mt5
import sys
import pandas as pd
import numpy as np


def connect():
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        quit()


def get_data(symbol, timeframe, n=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    if not rates:
        print(f"Failed to retrieve data for {symbol}.")
        return pd.DataFrame()  # Return an empty DataFrame in case of failure

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.set_index("time", inplace=True)
    print(df.tail())  # Print last few rows to check data
    return df


def calculate_moving_averages(df, short_window=5, long_window=20):
    df["SMA_short"] = df["close"].rolling(window=short_window, min_periods=1).mean()
    df["SMA_long"] = df["close"].rolling(window=long_window, min_periods=1).mean()


def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


def calculate_macd(df, short_period=12, long_period=26, signal_period=9):
    short_ema = df["close"].ewm(span=short_period, adjust=False).mean()
    long_ema = df["close"].ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal_line
    return macd.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]


def place_trade(symbol, volume, action, take_profit, stop_loss):
    # Convert action to MT5 order type
    if action.lower() == "buy":
        order_type = mt5.ORDER_TYPE_BUY
    elif action.lower() == "sell":
        order_type = mt5.ORDER_TYPE_SELL
    else:
        print(f"Invalid action: {action}")
        return

    # Get current price and check if symbol is available
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print(f"Failed to get tick info for symbol {symbol}.")
        return

    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info or not symbol_info.visible:
        print(f"Symbol {symbol} is not available or not visible.")
        return

    point = symbol_info.point
    min_stop_distance = symbol_info.stop_level * point

    # Calculate stop loss and take profit based on price and order type
    if order_type == mt5.ORDER_TYPE_BUY:
        sl = price - stop_loss * point
        tp = price + take_profit * point
    else:
        sl = price + stop_loss * point
        tp = price - take_profit * point

    # Validate stop loss and take profit against minimum stop distance
    if (abs(price - sl) < min_stop_distance) or (abs(tp - price) < min_stop_distance):
        print(f"Stop loss or take profit is too close to the current price.")
        print(f"Minimum stop distance: {min_stop_distance}, SL: {sl}, TP: {tp}")
        return

    # Create request parameters
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 234000,
        "comment": "Trade via API",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    print(f"Sending order with parameters: {request}")
    result = mt5.order_send(request)
    if result is None:
        print("Order send failed, no result returned")
        return

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order send failed, retcode = {result.retcode}")
        print(f"Result: {result}")
    else:
        print(f"Trade successful, result: {result}")


def analyze_market(
    symbol,
    short_window=5,
    long_window=20,
    rsi_period=14,
    macd_short_period=12,
    macd_long_period=26,
    macd_signal_period=9,
):
    df = get_data(symbol, mt5.TIMEFRAME_M15)
    calculate_moving_averages(df, short_window, long_window)
    rsi = calculate_rsi(df, rsi_period)
    macd, signal_line, histogram = calculate_macd(
        df, macd_short_period, macd_long_period, macd_signal_period
    )

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    if (
        last_row["SMA_short"] > last_row["SMA_long"]
        and prev_row["SMA_short"] <= prev_row["SMA_long"]
        and rsi < 30
    ):
        return "buy"
    elif (
        last_row["SMA_short"] < last_row["SMA_long"]
        and prev_row["SMA_short"] >= prev_row["SMA_long"]
        and rsi > 70
    ):
        return "sell"
    elif macd > signal_line:
        return "buy"
    elif macd < signal_line:
        return "sell"
    else:
        return "hold"


if __name__ == "__main__":
    if len(sys.argv) < 8:
        print(
            "Usage: python swing_trading.py <symbol> <volume> <action> <short_window> <long_window> <rsi_period> <macd_short_period> <macd_long_period> <macd_signal_period> mt5 file"
        )
        quit()

    symbol = sys.argv[1]
    volume = float(sys.argv[2])
    action = sys.argv[3]
    short_window = int(sys.argv[4])
    long_window = int(sys.argv[5])
    rsi_period = int(sys.argv[6])
    macd_short_period = int(sys.argv[7])
    macd_long_period = int(sys.argv[8])
    macd_signal_period = int(sys.argv[9])

    connect()

    action = analyze_market(
        symbol,
        short_window,
        long_window,
        rsi_period,
        macd_short_period,
        macd_long_period,
        macd_signal_period,
    )
    if action != "hold":
        print(f"Action determined: {action}")
        place_trade(symbol, volume, action)
    else:
        print("No action taken based on market analysis.")

    mt5.shutdown()

import MetaTrader5 as mt5
import sys
import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


# MetaTrader 5 connection and disconnection
def connect():
    if not mt5.initialize():
        logging.error(
            f"MetaTrader5 initialize() failed, error code = {mt5.last_error()}"
        )
        quit()
    else:
        logging.info("Connected to MetaTrader 5.")


def disconnect():
    mt5.shutdown()
    logging.info("Disconnected from MetaTrader 5.")


# Retrieve candlestick data
def get_candlestick_data(symbol, timeframe, count=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    if rates is None or len(rates) == 0:
        logging.error(
            f"Failed to retrieve data for {symbol}. Error: {mt5.last_error()}"
        )
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


# Preprocess data
def preprocess_data(df):
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(window=5).std()
    df["momentum"] = df["close"].diff(4)
    df["sma_10"] = df["close"].rolling(window=10).mean()
    df["sma_50"] = df["close"].rolling(window=50).mean()
    df["rsi"] = 100 - (
        100
        / (
            1
            + df["close"].diff().where(lambda x: x > 0, 0).rolling(window=14).mean()
            / df["close"]
            .diff()
            .where(lambda x: x < 0, 0)
            .abs()
            .rolling(window=14)
            .mean()
        )
    )
    return df.dropna()


# Train model
def train_model(data):
    data["target"] = (data["close"].shift(-1) > data["close"]).astype(int)
    features = data[
        [
            "open",
            "high",
            "low",
            "close",
            "volatility",
            "momentum",
            "sma_10",
            "sma_50",
            "rsi",
        ]
    ]
    target = data["target"].values

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    X_train, X_test, y_train, y_test = train_test_split(
        features_scaled, target, test_size=0.2, random_state=42
    )

    param_grid = {
        "n_estimators": [50, 100, 150],
        "max_depth": [None, 10, 20, 30],
        "min_samples_split": [2, 5, 10],
    }
    grid_search = GridSearchCV(
        RandomForestClassifier(random_state=42), param_grid, cv=5, scoring="accuracy"
    )
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    accuracy = accuracy_score(y_test, best_model.predict(X_test))
    logging.info(f"Model trained with accuracy: {accuracy:.2f}")

    joblib.dump(best_model, "price_action_model.pkl")
    joblib.dump(scaler, "scaler.pkl")

    return best_model


# Predict action
def predict_action(df, model_path="price_action_model.pkl", scaler_path="scaler.pkl"):
    features = df[
        [
            "open",
            "high",
            "low",
            "close",
            "volatility",
            "momentum",
            "sma_10",
            "sma_50",
            "rsi",
        ]
    ].tail(1)
    scaler = joblib.load(scaler_path)
    features_scaled = scaler.transform(features)

    model = joblib.load(model_path)
    prediction = model.predict(features_scaled)

    return "BUY" if prediction == 1 else "SELL" if prediction == 0 else None


# Calculate stop loss and take profit
def calculate_sltp(action, entry_price, stop_loss_pips, take_profit_pips, point):
    min_stop_loss = 10 * point
    min_take_profit = 10 * point

    if action == "BUY":
        stop_loss = entry_price - max(stop_loss_pips * point, min_stop_loss)
        take_profit = entry_price + max(take_profit_pips * point, min_take_profit)
    elif action == "SELL":
        stop_loss = entry_price + max(stop_loss_pips * point, min_stop_loss)
        take_profit = entry_price - max(take_profit_pips * point, min_take_profit)
    else:
        logging.error(f"Invalid action: {action}")
        return None, None

    return stop_loss, take_profit


# Validate trade parameters
def validate_trade_parameters(symbol, volume, price, sl, tp):
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        logging.error(f"Failed to retrieve symbol info for {symbol}.")
        return False

    min_volume = symbol_info.volume_min
    lot_step = symbol_info.volume_step
    point = symbol_info.point

    if volume < min_volume or (volume % lot_step != 0):
        logging.error(
            f"Invalid volume: {volume}. Must be a multiple of {lot_step} and at least {min_volume}."
        )
        return False
    if price <= 0:
        logging.error(f"Invalid price: {price}.")
        return False
    if sl <= 0 or tp <= 0:
        logging.error(f"Invalid SL or TP values after adjustment.")
        return False
    return True


# Place trade
def place_trade(symbol, volume, action, stop_loss, take_profit):
    action = action.upper()
    order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        logging.error(
            f"Failed to get tick info for symbol {symbol}. Error: {mt5.last_error()}"
        )
        return

    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info or not symbol_info.visible:
        logging.error(f"Symbol {symbol} is not available or not visible.")
        return

    point = symbol_info.point
    min_stop_level = (
        symbol_info.stop_level * point
        if hasattr(symbol_info, "stop_level")
        else 10 * point
    )

    sl = price - stop_loss if order_type == mt5.ORDER_TYPE_BUY else price + stop_loss
    tp = (
        price + take_profit if order_type == mt5.ORDER_TYPE_BUY else price - take_profit
    )

    if abs(price - sl) < min_stop_level:
        sl = price - min_stop_level
    if abs(tp - price) < min_stop_level:
        tp = price + min_stop_level

    if not validate_trade_parameters(symbol, volume, price, sl, tp):
        return

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

    logging.info(f"Sending order with parameters: {request}")
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(
            f"Order send failed, retcode = {result.retcode}. Comment: {result.comment}"
        )
    else:
        logging.info(f"Order placed successfully, result: {result}")


# Close position
def close_position(ticket, symbol, position_type, volume):
    price = (
        mt5.symbol_info_tick(symbol).bid
        if position_type == mt5.ORDER_TYPE_BUY
        else mt5.symbol_info_tick(symbol).ask
    )
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": (
            mt5.ORDER_TYPE_SELL
            if position_type == mt5.ORDER_TYPE_BUY
            else mt5.ORDER_TYPE_BUY
        ),
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "Close trade via API",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    logging.info(f"Closing position with request: {request}")
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(
            f"Position close failed, retcode = {result.retcode}. Comment: {result.comment}"
        )
    else:
        logging.info(f"Position closed successfully, result: {result}")


# Close all open positions
def close_all_positions(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        logging.error(
            f"Failed to get positions for symbol {symbol}. Error: {mt5.last_error()}"
        )
        return False

    if len(positions) == 0:
        logging.info(f"No open positions for {symbol}.")
        return True

    for position in positions:
        close_position(position.ticket, symbol, position.type, position.volume)

    logging.info(f"All positions for {symbol} have been closed.")
    return True


# Check if a new candle has started
def is_new_candle(df):
    latest_time = df["time"].iloc[-1]
    current_time = pd.to_datetime("now")
    time_diff = current_time - latest_time
    return time_diff.total_seconds() >= 60


# Manage trade with trailing stop loss
def close_trade_with_trailing_stop(symbol, trailing_stop_threshold=0.50):
    while True:
        positions = mt5.positions_get(symbol=symbol)
        if positions is None or len(positions) == 0:
            logging.info(f"No open positions for {symbol}.")
            return

        for position in positions:
            ticket = position.ticket
            profit_usd = position.profit
            logging.info(f"Current profit for position {ticket}: ${profit_usd:.2f} USD")

            if profit_usd >= trailing_stop_threshold:
                tick = mt5.symbol_info_tick(symbol)
                price = tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask
                point = mt5.symbol_info(symbol).point
                new_stop_loss = (
                    price - trailing_stop_threshold
                    if position.type == mt5.ORDER_TYPE_BUY
                    else price + trailing_stop_threshold
                )

                if (
                    position.type == mt5.ORDER_TYPE_BUY and new_stop_loss > position.sl
                ) or (
                    position.type == mt5.ORDER_TYPE_SELL and new_stop_loss < position.sl
                ):
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": symbol,
                        "position": ticket,
                        "sl": new_stop_loss,
                        "tp": position.tp,
                        "deviation": 10,
                        "magic": 234000,
                        "comment": "Trailing stop loss adjustment",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    result = mt5.order_send(request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        logging.error(
                            f"Failed to update stop loss for position {ticket}: {result.comment}"
                        )
                    else:
                        logging.info(
                            f"Updated stop loss for position {ticket} to {new_stop_loss:.2f}"
                        )

            if profit_usd >= target_profit_usd:
                logging.info(
                    f"Target profit reached for position {ticket}, closing the position."
                )
                close_position(ticket, symbol, position.type, position.volume)
                return

        time.sleep(10)  # Wait before rechecking to avoid rapid-fire execution


# Execute trading logic
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: python trading_bot.py <symbol> <volume> <stop_loss_pips> <take_profit_pips>"
        )
        quit()

    symbol = sys.argv[1]
    volume = float(sys.argv[2])
    stop_loss_pips = float(sys.argv[3])
    take_profit_pips = float(sys.argv[4])
    target_profit_usd = 1.0
    trailing_stop_threshold = 0.50

    connect()

    try:
        candlestick_data = get_candlestick_data(symbol, mt5.TIMEFRAME_M1, count=100)
        if candlestick_data.empty:
            logging.error("Failed to retrieve sufficient candlestick data.")
            disconnect()
            quit()

        processed_data = preprocess_data(candlestick_data)

        if processed_data.empty:
            logging.error("No data after preprocessing.")
            disconnect()
            quit()

        if is_new_candle(candlestick_data):
            if close_all_positions(symbol):
                try:
                    action = predict_action(processed_data)
                except FileNotFoundError:
                    logging.info("Model not found. Training a new model...")
                    train_model(processed_data)
                    action = predict_action(processed_data)

                if action:
                    logging.info(f"Action determined by the model: {action}")
                    symbol_info = mt5.symbol_info(symbol)
                    point = symbol_info.point
                    stop_loss, take_profit = calculate_sltp(
                        action,
                        processed_data.iloc[-1]["close"],
                        stop_loss_pips,
                        take_profit_pips,
                        point,
                    )
                    if stop_loss and take_profit:
                        place_trade(symbol, volume, action, stop_loss, take_profit)
                        close_trade_with_trailing_stop(symbol, trailing_stop_threshold)

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
    finally:
        disconnect()

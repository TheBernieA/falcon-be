import MetaTrader5 as mt5
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


# Function to connect to MetaTrader 5
def connect_mt5():
    if not mt5.initialize():
        logging.error(f"initialize() failed, error code = {mt5.last_error()}")
        return False
    return True


# Function to get all open trades
def get_open_trades():
    positions = mt5.positions_get()
    if positions is None:
        logging.error("Failed to retrieve positions.")
        return []
    return [pos._asdict() for pos in positions]


# Function to close all open trades
def close_all_trades():
    positions = mt5.positions_get()
    if positions is None:
        logging.error("Failed to retrieve positions.")
        return {"error": "Failed to retrieve positions."}

    for position in positions:
        ticket = position.ticket
        action = mt5.TRADE_ACTION_DEAL
        volume = position.volume
        position_type = position.type
        price = (
            mt5.symbol_info_tick(position.symbol).bid
            if position_type == mt5.ORDER_TYPE_BUY
            else mt5.symbol_info_tick(position.symbol).ask
        )

        close_request = {
            "action": action,
            "symbol": position.symbol,
            "volume": volume,
            "type": (
                mt5.ORDER_TYPE_SELL
                if position_type == mt5.ORDER_TYPE_BUY
                else mt5.ORDER_TYPE_BUY
            ),
            "position": ticket,
            "price": price,
            "deviation": 10,
            "magic": 234000,
            "comment": "Close trade via API",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(close_request)
        if result is None:
            logging.error(
                f"Failed to close position {ticket}: No response from order_send"
            )
            return {
                "error": f"Failed to close position {ticket}: No response from order_send"
            }
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"Failed to close position {ticket}: {result.comment}")
            return {"error": f"Failed to close position {ticket}: {result.comment}"}
        else:
            logging.info(f"Successfully closed position {ticket}")

    return {"status": "All trades closed successfully"}


# Function to close trades in profit
def close_trades_in_profit():
    positions = mt5.positions_get()
    if positions is None:
        logging.error("Failed to retrieve positions.")
        return {"error": "Failed to retrieve positions."}

    for position in positions:
        ticket = position.ticket
        profit = position.profit

        if profit > 0:
            action = mt5.TRADE_ACTION_DEAL
            volume = position.volume
            position_type = position.type
            symbol = position.symbol
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logging.error(f"Failed to get symbol tick info for {symbol}")
                continue

            price = tick.bid if position_type == mt5.ORDER_TYPE_BUY else tick.ask

            close_request = {
                "action": action,
                "symbol": symbol,
                "volume": volume,
                "type": (
                    mt5.ORDER_TYPE_SELL
                    if position_type == mt5.ORDER_TYPE_BUY
                    else mt5.ORDER_TYPE_BUY
                ),
                "position": ticket,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "comment": "Close profit trade",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            logging.info(f"Attempting to send close request: {close_request}")

            result = mt5.order_send(close_request)
            if result is None:
                error_message = mt5.last_error()
                logging.error(
                    f"Failed to close profitable position {ticket}: No response from order_send. Error: {error_message}"
                )
                continue  # Skip to the next position
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(
                    f"Failed to close profitable position {ticket}: {result.comment}"
                )
                continue  # Skip to the next position
            logging.info(f"Successfully closed profitable position {ticket}")

    return {"status": "All profitable trades closed successfully"}


# Function to close trades in loss
def close_trades_in_loss():
    positions = mt5.positions_get()
    if positions is None:
        logging.error("Failed to retrieve positions.")
        return {"error": "Failed to retrieve positions."}

    for position in positions:
        ticket = position.ticket
        profit = position.profit

        if profit < 0:
            action = mt5.TRADE_ACTION_DEAL
            volume = position.volume
            position_type = position.type
            price = (
                mt5.symbol_info_tick(position.symbol).bid
                if position_type == mt5.ORDER_TYPE_BUY
                else mt5.symbol_info_tick(position.symbol).ask
            )

            close_request = {
                "action": action,
                "symbol": position.symbol,
                "volume": volume,
                "type": (
                    mt5.ORDER_TYPE_SELL
                    if position_type == mt5.ORDER_TYPE_BUY
                    else mt5.ORDER_TYPE_BUY
                ),
                "position": ticket,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "comment": "Close losing trade via API",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(close_request)
            if result is None:
                logging.error(
                    f"Failed to close losing position {ticket}: No response from order_send"
                )
                return {
                    "error": f"Failed to close losing position {ticket}: No response from order_send"
                }
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(
                    f"Failed to close losing position {ticket}: {result.comment}"
                )
                return {
                    "error": f"Failed to close losing position {ticket}: {result.comment}"
                }
            else:
                logging.info(f"Successfully closed losing position {ticket}")

    return {"status": "All losing trades closed successfully"}


# Function to check if autotrade is active
def is_autotrade_active():
    account_info = mt5.account_info()
    if account_info is None:
        logging.error("Failed to retrieve account info.")
        return {"error": "Failed to retrieve account info."}
    trading_enabled = account_info.trade_allowed
    return {"autotrade_active": trading_enabled}


# Function to enable or disable autotrade
def set_autotrade(status):
    # Simulating enabling/disabling autotrade
    if status:
        logging.info("Autotrade is now enabled.")
    else:
        logging.info("Autotrade is now disabled.")
    return {"status": f"Autotrade {'enabled' if status else 'disabled'}"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mt5_trade_manager.py <command> [<status>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "get_open_trades":
        if connect_mt5():
            trades = get_open_trades()
            mt5.shutdown()
            print(json.dumps(trades))
        else:
            print(json.dumps({"error": "Failed to connect to MT5"}))
    elif command == "close_all_trades":
        if connect_mt5():
            success = close_all_trades()
            mt5.shutdown()
            if success:
                print(json.dumps({"status": "All trades closed successfully"}))
            else:
                print(json.dumps({"error": "Failed to close all trades"}))
        else:
            print(json.dumps({"error": "Failed to connect to MT5"}))
    elif command == "close_trades_in_profit":
        if connect_mt5():
            success = close_trades_in_profit()
            mt5.shutdown()
            if success:
                print(
                    json.dumps({"status": "All profitable trades closed successfully"})
                )
            else:
                print(json.dumps({"error": "Failed to close profitable trades"}))
        else:
            print(json.dumps({"error": "Failed to connect to MT5"}))
    elif command == "close_trades_in_loss":
        if connect_mt5():
            success = close_trades_in_loss()
            mt5.shutdown()
            if success:
                print(json.dumps({"status": "All losing trades closed successfully"}))
            else:
                print(json.dumps({"error": "Failed to close losing trades"}))
        else:
            print(json.dumps({"error": "Failed to connect to MT5"}))
    elif command == "is_autotrade_active":
        if connect_mt5():
            active = is_autotrade_active()
            mt5.shutdown()
            print(json.dumps(active))
        else:
            print(json.dumps({"error": "Failed to connect to MT5"}))
    elif command == "set_autotrade":
        if len(sys.argv) != 3:
            print("Usage: python mt5_trade_manager.py set_autotrade <status>")
            sys.exit(1)
        status = sys.argv[2].lower() in ["true", "1", "yes"]
        if connect_mt5():
            result = set_autotrade(status)
            mt5.shutdown()
            print(json.dumps(result))
        else:
            print(json.dumps({"error": "Failed to connect to MT5"}))
    else:
        print("Unknown command")

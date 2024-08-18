import MetaTrader5 as mt5
import sys
import json

# Global variable to keep track of login status
is_logged_in = False

def initialize_mt5():
    """Initialize the MT5 connection."""
    if not mt5.initialize():
        error_msg = f"Initialize() failed, error code = {mt5.last_error()}"
        print(error_msg)
        return False
    return True

def mt5_login(login, password, server):
    """Login to MT5 with provided credentials and server."""
    global is_logged_in
    
    # Initialize MT5 connection
    if not initialize_mt5():
        return {"success": False, "error": "Initialization failed"}
    
    # Attempt to login
    authorized = mt5.login(login, password=password, server=server)
    if not authorized:
        error_msg = f"Failed to connect to account #{login}, error code: {mt5.last_error()}"
        print(error_msg)
        mt5.shutdown()
        return {"success": False, "error": error_msg}
    
    is_logged_in = True
    return {"success": True}

if __name__ == "__main__":
    # Extract arguments
    if len(sys.argv) != 4:
        print(json.dumps({"success": False, "error": "Invalid number of arguments"}))
        sys.exit(1)
    
    login = int(sys.argv[1])
    password = sys.argv[2]
    server = sys.argv[3]

    # Perform login
    result = mt5_login(login, password, server)
    
    # Shutdown MT5 connection
    if is_logged_in:
        mt5.shutdown()
    
    print(json.dumps(result))

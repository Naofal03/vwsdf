import MetaTrader5 as mt5

def connect_to_mt5(login, password, server):
    if not mt5.initialize(login=login, password=password, server=server):
        error_code, error_message = mt5.last_error()
        print(f"Erreur de connexion à MT5 : {error_code} - {error_message}")
        raise ConnectionError("Failed to connect to MetaTrader 5")
    print("Connexion réussie à MetaTrader 5")
    return True

def disconnect_mt5():
    print("Déconnexion de MetaTrader 5...")
    mt5.shutdown()
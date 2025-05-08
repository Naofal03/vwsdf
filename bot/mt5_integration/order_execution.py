import MetaTrader5 as mt5

def place_order(symbol, volume, order_type, price=None):
    # Définir le type d'ordre (achat ou vente)
    order_type_map = {
        "BUY": mt5.ORDER_BUY,
        "SELL": mt5.ORDER_SELL
    }
    order_type_mt5 = order_type_map.get(order_type.upper())
    if not order_type_mt5:
        raise ValueError("Type d'ordre invalide. Utilisez 'BUY' ou 'SELL'.")

    # Préparer la requête d'ordre
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type_mt5,
        "price": price or mt5.symbol_info_tick(symbol).ask,
        "deviation": 10,
        "magic": 123456,
        "comment": "Automated trade",
    }

    # Envoyer l'ordre
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Erreur lors de l'envoi de l'ordre : {result.retcode}")
    return result
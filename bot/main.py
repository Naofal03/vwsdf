from analysis.fundamental_analysis import fetch_news, analyze_news
from analysis.technical_analysis import calculate_indicators, detect_price_action, process_zones
from analysis.mathematical_model import train_model, predict_price
from mt5_integration.mt5_connection import connect_to_mt5, disconnect_mt5
from mt5_integration.order_execution import place_order
from notion_integration.trade_journal import log_trade_to_notion
import json
import shutil
import os

def get_market_data(symbol, timeframe):
    print(f"Récupération des données de marché pour {symbol} sur le timeframe {timeframe}...")

    import MetaTrader5 as mt5
    from datetime import datetime, timedelta

    # Vérifier la connexion à MT5
    if not mt5.initialize():
        print("Erreur : Impossible d'initialiser la connexion à MetaTrader 5.")
        return None

    # Vérifier si le symbole est disponible
    if not mt5.symbol_select(symbol, True):
        print(f"Erreur : Le symbole {symbol} n'est pas disponible ou n'a pas pu être sélectionné.")
        mt5.shutdown()
        return None

    # Map des timeframes MQL5
    timeframes = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,  # Ajout du timeframe M30
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }

    if timeframe not in timeframes:
        print(f"Erreur : Timeframe {timeframe} non valide.")
        mt5.shutdown()
        return None

    # Récupérer la première date disponible pour ce symbole
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 10)  # Essayer de récupérer les 10 dernières années
        print(f"Paramètres : Symbole = {symbol}, Timeframe = {timeframes[timeframe]}, Date de début = {start_date}, Date de fin = {end_date}")
        rates = mt5.copy_rates_range(symbol, timeframes[timeframe], start_date, end_date)
        
        # Vérifier si des données sont disponibles
        if rates is None or len(rates) == 0:
            print(f"Erreur : Aucune donnée de marché disponible pour {symbol} sur le timeframe {timeframe} entre {start_date} et {end_date}.")
            mt5.shutdown()
            return None

    except Exception as e:
        print(f"Erreur lors de la récupération des données de marché : {e}")
        mt5.shutdown()
        return None

    print(f"Données de marché récupérées avec succès pour {symbol}. Nombre de bougies : {len(rates)}")
    mt5.shutdown()
    return {
        'close': [rate['close'] for rate in rates],
        'open': [rate['open'] for rate in rates],
        'high': [rate['high'] for rate in rates],
        'low': [rate['low'] for rate in rates],
        'time': [datetime.fromtimestamp(rate['time']) for rate in rates]}

def copy_zones_to_mt5():
    print("Copie du fichier zones.json dans le dossier MT5...")
    source = os.path.abspath("zones.json")  # Utiliser un chemin absolu
    mt5_folder = os.path.expanduser("~") + "/AppData/Roaming/MetaQuotes/Terminal/"
    terminal_folders = [f for f in os.listdir(mt5_folder) if os.path.isdir(os.path.join(mt5_folder, f))]
    
    if not terminal_folders:
        print("Erreur : Aucun dossier MT5 trouvé dans AppData/Roaming/MetaQuotes/Terminal/")
        raise FileNotFoundError("Aucun dossier MT5 trouvé.")
    
    destination = os.path.join(mt5_folder, terminal_folders[0], "MQL5", "Files", "zones.json")
    shutil.copy(source, destination)
    print(f"Fichier zones.json copié dans : {destination}")

def generate_zones_file(market_data):
    print("Lecture des informations de la paire et du timeframe depuis zones.json...")
    zones = {
        "support": [],
        "resistance": [],
        "bullish_order_blocks": [],
        "bearish_order_blocks": [],
        "equal_highs": [],
        "equal_lows": [],
        "trendlines": [],
        "imbalances": []
    }

    # Détection des supports et résistances
    for i in range(1, len(market_data['low']) - 1):
        if market_data['low'][i] < market_data['low'][i - 1] and market_data['low'][i] < market_data['low'][i + 1]:
            zones["support"].append(market_data['low'][i])
        if market_data['high'][i] > market_data['high'][i - 1] and market_data['high'][i] > market_data['high'][i + 1]:
            zones["resistance"].append(market_data['high'][i])

    # Sauvegarder les zones dans zones.json
    with open("zones.json", "w") as file:
        json.dump(zones, file, indent=4)
    print("Zones générées avec succès.")

def delete_old_mql5_script():
    print("Suppression de l'ancien fichier chart_tracing.mq5...")
    mt5_folder = os.path.expanduser("~") + "/AppData/Roaming/MetaQuotes/Terminal/"
    terminal_folders = [f for f in os.listdir(mt5_folder) if os.path.isdir(os.path.join(mt5_folder, f))]
    
    if not terminal_folders:
        print("Erreur : Aucun dossier MT5 trouvé dans AppData/Roaming/MetaQuotes/Terminal/")
        return
    
    script_path = os.path.join(mt5_folder, terminal_folders[0], "MQL5", "Scripts", "chart_tracing.mq5")
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"Ancien fichier supprimé : {script_path}")
    else:
        print("Aucun fichier chart_tracing.mq5 à supprimer.")

def main():
    print("Début du programme principal...")
    # Connexion à MT5
    try:
        login = 40628821
        password = "Papillon12.Fr"
        server = "Deriv-Demo"
        print(f"Tentative de connexion avec login={login}, password={password}, server={server}...")
        connect_to_mt5(login=login, password=password, server=server)
        print("Connexion réussie à MT5.")
    except ConnectionError as e:
        print(f"Erreur de connexion : {e}")
        return

    # Lire la paire et le timeframe depuis zones.json
    try:
        with open("zones.json", "r") as file:
            data = json.load(file)
            symbol = data.get("symbol", "EURUSD")  # Par défaut EURUSD
            timeframe = data.get("timeframe", "M30")  # Par défaut M30
    except FileNotFoundError:
        print("Fichier zones.json introuvable. Utilisation des valeurs par défaut.")
        symbol = "EURUSD"
        timeframe = "M15"

    print(f"Utilisation de la paire {symbol} et du timeframe {timeframe}.")

    # Récupération des données de marché
    try:
        market_data = get_market_data(symbol, timeframe)
        if market_data is None:
            print("Erreur : Les données de marché n'ont pas pu être récupérées.")
            disconnect_mt5()
            return
    except Exception as e:
        print(f"Erreur lors de la récupération des données de marché : {e}")
        disconnect_mt5()
        return

    # Génération du fichier zones.json
    try:
        generate_zones_file(market_data)  # Passer les données de marché pour calculer les zones
    except Exception as e:
        print(f"Erreur lors de la génération du fichier zones.json : {e}")
        disconnect_mt5()
        return

    # Exemple de copie des zones
    try:
        copy_zones_to_mt5()
    except Exception as e:
        print(f"Erreur lors de la copie des zones : {e}")
        disconnect_mt5()
        return

    # Suppression de l'ancien fichier chart_tracing.mq5
    delete_old_mql5_script()

    # Déconnexion
    print("Déconnexion de MT5...")
    disconnect_mt5()
    print("Programme terminé avec succès.")

if __name__ == "__main__":
    main()

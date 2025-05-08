import pandas as pd
import json

def calculate_indicators(data):
    # Calcul des indicateurs techniques
    sma = calculate_sma(data['close'], period=50)
    ema = calculate_ema(data['close'], period=20)
    rsi = calculate_rsi(data['close'], period=14)
    return {'SMA': sma, 'EMA': ema, 'RSI': rsi}

def calculate_sma(data, period):
    return pd.Series(data).rolling(window=period).mean().tolist()

def calculate_ema(data, period):
    return pd.Series(data).ewm(span=period, adjust=False).mean().tolist()

def calculate_rsi(data, period=14):
    delta = pd.Series(data).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.tolist()

def detect_price_action(data):
    # Détection des modèles de Price Action
    patterns = []
    if is_bullish_engulfing(data):
        patterns.append("Bullish Engulfing")
    return patterns

def is_bullish_engulfing(data):
    # Exemple de détection d'un modèle
    return data['open'][-1] < data['close'][-1] and data['open'][-2] > data['close'][-2]

def detect_zones(data):
    # Détection des zones de support et de résistance
    support = min(data['low'][-50:])  # Exemple : plus bas des 50 dernières bougies
    resistance = max(data['high'][-50:])  # Exemple : plus haut des 50 dernières bougies
    return {'support': support, 'resistance': resistance}

def export_zones_to_file(zones, filepath="zones.json"):
    # Exporter les zones dans un fichier JSON
    with open(filepath, 'w') as file:
        json.dump(zones, file)

# Exemple d'utilisation
def process_zones(data):
    zones = detect_zones(data)
    export_zones_to_file(zones)
    return zones
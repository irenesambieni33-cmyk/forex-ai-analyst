# ============================================================
# FOREX AI ANALYST
# Configuration générale du projet
# ============================================================

# ------------------------------------------------------------
# INSTRUMENTS
# ------------------------------------------------------------

INSTRUMENTS = {
    "EUR/USD": {
        "ticker": "EURUSD=X",
        "name": "Euro / Dollar américain",
    },
    "XAU/USD": {
        "ticker": "XAUUSD=X",
        "name": "Or / Dollar américain",
    },
}


# ------------------------------------------------------------
# TIMEFRAMES
# ------------------------------------------------------------

TIMEFRAMES = {
    "D1": {
        "interval": "1d",
        "period": "1y",
        "weight": 3,
        "role": "Contexte principal",
    },

    "H4": {
        "interval": "1h",
        "period": "3mo",
        "weight": 3,
        "role": "Tendance principale",
    },

    "H1": {
        "interval": "1h",
        "period": "3mo",
        "weight": 2,
        "role": "Confirmation",
    },

    "M15": {
        "interval": "15m",
        "period": "1mo",
        "weight": 1,
        "role": "Préparation de l'entrée",
    },

    "M5": {
        "interval": "5m",
        "period": "5d",
        "weight": 1,
        "role": "Confirmation d'entrée",
    },
}


# ------------------------------------------------------------
# ORDRE DES TIMEFRAMES
# ------------------------------------------------------------

TIMEFRAME_ORDER = [
    "D1",
    "H4",
    "H1",
    "M15",
    "M5",
]


# ------------------------------------------------------------
# INDICATEURS
# ------------------------------------------------------------

INDICATOR_SETTINGS = {

    # Moyennes mobiles
    "EMA_FAST": 20,
    "EMA_SLOW": 50,
    "SMA_LONG": 200,

    # RSI
    "RSI_PERIOD": 14,

    # MACD
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,

    # ATR
    "ATR_PERIOD": 14,

    # ADX
    "ADX_PERIOD": 14,

    # Bollinger Bands
    "BB_PERIOD": 20,
    "BB_STD": 2,

    # Stochastic
    "STOCH_K": 14,
    "STOCH_D": 3,
}


# ------------------------------------------------------------
# FIBONACCI
# ------------------------------------------------------------

FIBONACCI_LEVELS = [
    0.236,
    0.382,
    0.500,
    0.618,
    0.786,
    1.272,
    1.618,
]


# ------------------------------------------------------------
# GESTION DU RISQUE
# ------------------------------------------------------------

RISK_SETTINGS = {

    # Risque maximum théorique par position
    "RISK_PER_TRADE": 0.01,

    # Risque cumulé maximum
    "MAX_TOTAL_RISK": 0.02,

    # Ratio risque/rendement minimum
    "MIN_RISK_REWARD": 2.0,
}


# ------------------------------------------------------------
# SEUILS DE DÉCISION
# ------------------------------------------------------------

DECISION_SETTINGS = {

    # Score minimum pour une décision d'achat
    "BUY_THRESHOLD": 4.0,

    # Score maximum pour une décision de vente
    "SELL_THRESHOLD": -4.0,

    # En dessous de ces seuils :
    # ATTENDRE / AUCUN SETUP
}


# ------------------------------------------------------------
# STRUCTURE DU MARCHÉ
# ------------------------------------------------------------

STRUCTURE_SETTINGS = {

    # Nombre de bougies utilisées pour identifier
    # les swings du marché
    "SWING_LOOKBACK": 3,

    # Nombre minimum de bougies historiques
    # nécessaires avant l'analyse
    "MIN_DATA_ROWS": 250,
}


# ------------------------------------------------------------
# APPLICATION
# ------------------------------------------------------------

APP_SETTINGS = {

    "TITLE": "Forex AI Analyst",

    "SUBTITLE": (
        "Analyse technique multi-timeframe "
        "avec gestion du risque"
    ),

    "VERSION": "V3",

    # Aucune exécution automatique d'ordres
    "AUTO_TRADING": False,
}
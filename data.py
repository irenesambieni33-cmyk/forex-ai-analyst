# ============================================================
# FOREX AI ANALYST
# data.py
# Gestion et préparation des données de marché
# ============================================================

import pandas as pd
import yfinance as yf


# ============================================================
# TÉLÉCHARGEMENT DES DONNÉES
# ============================================================

def download_market_data(
    ticker: str,
    interval: str = "1h",
    period: str = "3mo"
) -> pd.DataFrame:
    """
    Télécharge les données historiques depuis Yahoo Finance.

    Parameters
    ----------
    ticker : str
        Symbole Yahoo Finance, par exemple EURUSD=X.

    interval : str
        Intervalle des bougies.

    period : str
        Période historique demandée.

    Returns
    -------
    pd.DataFrame
        Données OHLCV nettoyées.
    """

    try:
        data = yf.download(
            ticker,
            interval=interval,
            period=period,
            auto_adjust=False,
            progress=False,
        )

    except Exception as error:
        print(f"Erreur lors du téléchargement de {ticker}: {error}")
        return pd.DataFrame()

    if data is None or data.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Gestion des colonnes MultiIndex de Yahoo Finance
    # --------------------------------------------------------

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # --------------------------------------------------------
    # Normalisation des noms de colonnes
    # --------------------------------------------------------

    data.columns = [
        str(column).strip().title()
        for column in data.columns
    ]

    # --------------------------------------------------------
    # Vérification des colonnes essentielles
    # --------------------------------------------------------

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    for column in required_columns:
        if column not in data.columns:
            return pd.DataFrame()

    # --------------------------------------------------------
    # Conservation des colonnes utiles
    # --------------------------------------------------------

    available_columns = [
        column
        for column in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
        if column in data.columns
    ]

    data = data[available_columns].copy()

    # --------------------------------------------------------
    # Conversion numérique
    # --------------------------------------------------------

    for column in available_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Suppression des données invalides
    # --------------------------------------------------------

    data = data.dropna(
        subset=[
            "Open",
            "High",
            "Low",
            "Close",
        ]
    )

    # --------------------------------------------------------
    # Suppression des doublons
    # --------------------------------------------------------

    data = data[~data.index.duplicated(keep="last")]

    # --------------------------------------------------------
    # Tri chronologique
    # --------------------------------------------------------

    data = data.sort_index()

    return data


# ============================================================
# NETTOYAGE DES DONNÉES
# ============================================================

def clean_market_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie un DataFrame OHLCV existant.
    """

    if data is None or data.empty:
        return pd.DataFrame()

    cleaned = data.copy()

    # Vérification des colonnes principales
    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in cleaned.columns
    ]

    if missing_columns:
        return pd.DataFrame()

    # Conversion numérique
    for column in cleaned.columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="coerce"
        )

    # Suppression des lignes incomplètes
    cleaned = cleaned.dropna(
        subset=required_columns
    )

    # Suppression des doublons
    cleaned = cleaned[
        ~cleaned.index.duplicated(keep="last")
    ]

    # Tri chronologique
    cleaned = cleaned.sort_index()

    return cleaned


# ============================================================
# RESAMPLING H4
# ============================================================

def resample_h4(data: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme des données H1 en bougies H4.

    Les données doivent contenir :
    Open, High, Low, Close et éventuellement Volume.
    """

    if data is None or data.empty:
        return pd.DataFrame()

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    for column in required_columns:
        if column not in data.columns:
            return pd.DataFrame()

    aggregation = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
    }

    if "Volume" in data.columns:
        aggregation["Volume"] = "sum"

    h4 = data.resample("4h").agg(aggregation)

    # Suppression des bougies incomplètes
    h4 = h4.dropna(
        subset=[
            "Open",
            "High",
            "Low",
            "Close",
        ]
    )

    return h4


# ============================================================
# CHARGEMENT D'UN TIMEFRAME
# ============================================================

def load_timeframe_data(
    ticker: str,
    timeframe: str,
) -> pd.DataFrame:
    """
    Charge les données correspondant à un timeframe.

    Timeframes pris en charge :
        D1
        H4
        H1
        M15
        M5
    """

    timeframe_config = {
        "D1": {
            "interval": "1d",
            "period": "1y",
        },

        "H4": {
            "interval": "1h",
            "period": "3mo",
        },

        "H1": {
            "interval": "1h",
            "period": "3mo",
        },

        "M15": {
            "interval": "15m",
            "period": "1mo",
        },

        "M5": {
            "interval": "5m",
            "period": "5d",
        },
    }

    if timeframe not in timeframe_config:
        return pd.DataFrame()

    config = timeframe_config[timeframe]

    data = download_market_data(
        ticker=ticker,
        interval=config["interval"],
        period=config["period"],
    )

    if data.empty:
        return data

    # H4 : conversion depuis H1
    if timeframe == "H4":
        data = resample_h4(data)

    return clean_market_data(data)


# ============================================================
# DERNIER PRIX
# ============================================================

def get_last_price(data: pd.DataFrame):
    """
    Retourne le dernier prix de clôture disponible.
    """

    if data is None or data.empty:
        return None

    if "Close" not in data.columns:
        return None

    last_close = data["Close"].iloc[-1]

    if pd.isna(last_close):
        return None

    return float(last_close)


# ============================================================
# INFORMATIONS SUR LES DONNÉES
# ============================================================

def get_data_info(data: pd.DataFrame) -> dict:
    """
    Retourne quelques informations utiles
    sur les données chargées.
    """

    if data is None or data.empty:
        return {
            "rows": 0,
            "first_date": None,
            "last_date": None,
        }

    return {
        "rows": len(data),
        "first_date": data.index[0],
        "last_date": data.index[-1],
    }
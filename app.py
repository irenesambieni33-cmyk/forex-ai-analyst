import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Forex AI Analyst",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.75;
        margin-bottom: 25px;
    }

    .signal-buy {
        padding: 18px;
        border-radius: 12px;
        background-color: rgba(0, 180, 80, 0.15);
        border: 1px solid rgba(0, 180, 80, 0.45);
        text-align: center;
        font-size: 28px;
        font-weight: 800;
    }

    .signal-sell {
        padding: 18px;
        border-radius: 12px;
        background-color: rgba(220, 50, 50, 0.15);
        border: 1px solid rgba(220, 50, 50, 0.45);
        text-align: center;
        font-size: 28px;
        font-weight: 800;
    }

    .signal-wait {
        padding: 18px;
        border-radius: 12px;
        background-color: rgba(240, 170, 0, 0.15);
        border: 1px solid rgba(240, 170, 0, 0.45);
        text-align: center;
        font-size: 28px;
        font-weight: 800;
    }

    .signal-none {
        padding: 18px;
        border-radius: 12px;
        background-color: rgba(150, 150, 150, 0.15);
        border: 1px solid rgba(150, 150, 150, 0.45);
        text-align: center;
        font-size: 28px;
        font-weight: 800;
    }

    .info-box {
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(100, 100, 100, 0.08);
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITRE
# ============================================================

st.markdown(
    '<div class="main-title">📊 Forex AI Analyst</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Analyse technique multi-timeframe • Aucun ordre automatique</div>',
    unsafe_allow_html=True
)


# ============================================================
# PARAMÈTRES
# ============================================================

INSTRUMENTS = {
    "EUR/USD": "EURUSD=X",
    "XAU/USD": "XAUUSD=X"
}

TIMEFRAMES = {
    "D1": {
        "interval": "1d",
        "period": "1y",
        "weight": 3
    },
    "H4": {
        "interval": "1h",
        "period": "3mo",
        "weight": 3
    },
    "H1": {
        "interval": "1h",
        "period": "3mo",
        "weight": 2
    },
    "M15": {
        "interval": "15m",
        "period": "1mo",
        "weight": 1
    },
    "M5": {
        "interval": "5m",
        "period": "5d",
        "weight": 1
    }
}


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def clean_dataframe(df):
    """Nettoie les données Yahoo Finance."""

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # Gestion des colonnes MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    required = ["Open", "High", "Low", "Close"]

    for column in required:
        if column not in df.columns:
            return pd.DataFrame()

    if "Volume" not in df.columns:
        df["Volume"] = 0

    df = df[["Open", "High", "Low", "Close", "Volume"]]

    df = df.dropna()

    return df


def download_data(ticker, interval, period):
    """Télécharge les données depuis Yahoo Finance."""

    try:
        data = yf.download(
            ticker,
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=False
        )

        return clean_dataframe(data)

    except Exception:
        return pd.DataFrame()


def resample_h4(df):
    """Transforme les bougies H1 en bougies H4."""

    if df.empty:
        return df

    data = df.copy()

    # Retirer timezone pour faciliter le resampling
    try:
        if getattr(data.index, "tz", None) is not None:
            data.index = data.index.tz_localize(None)
    except Exception:
        pass

    h4 = data.resample("4h", label="right", closed="right").agg(
        {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum"
        }
    )

    h4 = h4.dropna()

    return h4


# ============================================================
# INDICATEURS
# ============================================================

def ema(series, period):
    return series.ewm(
        span=period,
        adjust=False,
        min_periods=period
    ).mean()


def sma(series, period):
    return series.rolling(
        window=period,
        min_periods=period
    ).mean()


def calculate_rsi(close, period=14):
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(close):
    fast = ema(close, 12)
    slow = ema(close, 26)

    macd = fast - slow
    signal = ema(macd, 9)

    histogram = macd - signal

    return macd, signal, histogram


def calculate_atr(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    previous_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - previous_close).abs()
    tr3 = (low - previous_close).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = true_range.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    return atr


def calculate_adx(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = pd.Series(
        np.where(
            (up_move > down_move) & (up_move > 0),
            up_move,
            0
        ),
        index=df.index
    )

    minus_dm = pd.Series(
        np.where(
            (down_move > up_move) & (down_move > 0),
            down_move,
            0
        ),
        index=df.index
    )

    previous_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - previous_close).abs()
    tr3 = (low - previous_close).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = tr.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    plus_di = (
        100
        * plus_dm.ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period
        ).mean()
        / atr
    )

    minus_di = (
        100
        * minus_dm.ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period
        ).mean()
        / atr
    )

    denominator = (plus_di + minus_di).replace(0, np.nan)

    dx = (
        100
        * (plus_di - minus_di).abs()
        / denominator
    )

    adx = dx.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    return adx, plus_di, minus_di


def calculate_bollinger(close, period=20, std_multiplier=2):
    middle = close.rolling(
        period,
        min_periods=period
    ).mean()

    std = close.rolling(
        period,
        min_periods=period
    ).std()

    upper = middle + std_multiplier * std
    lower = middle - std_multiplier * std

    return middle, upper, lower


def calculate_stochastic(df, period=14, smooth=3):
    lowest_low = df["Low"].rolling(
        period,
        min_periods=period
    ).min()

    highest_high = df["High"].rolling(
        period,
        min_periods=period
    ).max()

    denominator = (
        highest_high - lowest_low
    ).replace(0, np.nan)

    k = (
        100
        * (df["Close"] - lowest_low)
        / denominator
    )

    d = k.rolling(
        smooth,
        min_periods=smooth
    ).mean()

    return k, d


# ============================================================
# STRUCTURE DU MARCHÉ
# ============================================================

def detect_swings(df, lookback=3):
    """Détecte des swing highs et swing lows simples."""

    data = df.copy()

    data["Swing_High"] = False
    data["Swing_Low"] = False

    if len(data) < (lookback * 2 + 1):
        return data

    highs = data["High"].values
    lows = data["Low"].values

    for i in range(lookback, len(data) - lookback):

        current_high = highs[i]
        current_low = lows[i]

        left_highs = highs[
            i - lookback:i
        ]

        right_highs = highs[
            i + 1:i + lookback + 1
        ]

        left_lows = lows[
            i - lookback:i
        ]

        right_lows = lows[
            i + 1:i + lookback + 1
        ]

        if (
            current_high > left_highs.max()
            and current_high > right_highs.max()
        ):
            data.iloc[
                i,
                data.columns.get_loc("Swing_High")
            ] = True

        if (
            current_low < left_lows.min()
            and current_low < right_lows.min()
        ):
            data.iloc[
                i,
                data.columns.get_loc("Swing_Low")
            ] = True

    return data


def classify_structure(df):
    """
    Classe une structure simplifiée :
    HH, HL, LH, LL.
    """

    data = detect_swings(df)

    swing_highs = data[
        data["Swing_High"]
    ]

    swing_lows = data[
        data["Swing_Low"]
    ]

    high_labels = []
    low_labels = []

    previous_high = None
    previous_low = None

    for idx, row in swing_highs.iterrows():

        current = row["High"]

        if previous_high is None:
            label = "H"
        elif current > previous_high:
            label = "HH"
        else:
            label = "LH"

        high_labels.append(
            (idx, label, current)
        )

        previous_high = current

    for idx, row in swing_lows.iterrows():

        current = row["Low"]

        if previous_low is None:
            label = "L"
        elif current > previous_low:
            label = "HL"
        else:
            label = "LL"

        low_labels.append(
            (idx, label, current)
        )

        previous_low = current

    structure = "NEUTRE"

    recent_highs = high_labels[-2:]
    recent_lows = low_labels[-2:]

    if len(recent_highs) >= 2 and len(recent_lows) >= 2:

        high1 = recent_highs[-2][1]
        high2 = recent_highs[-1][1]

        low1 = recent_lows[-2][1]
        low2 = recent_lows[-1][1]

        if (
            high2 == "HH"
            and low2 == "HL"
        ):
            structure = "HAUSSIÈRE"

        elif (
            high2 == "LH"
            and low2 == "LL"
        ):
            structure = "BAISSIÈRE"

    return data, high_labels, low_labels, structure


def detect_bos(df):
    """
    Détection simplifiée d'un potentiel Break of Structure.
    """

    if len(df) < 20:
        return "AUCUN"

    data = detect_swings(df)

    swing_highs = data[
        data["Swing_High"]
    ]

    swing_lows = data[
        data["Swing_Low"]
    ]

    close = data["Close"].iloc[-1]

    bos = "AUCUN"

    if not swing_highs.empty:
        recent_high = swing_highs["High"].iloc[-1]

        if close > recent_high:
            bos = "BOS HAUSSIER"

    if not swing_lows.empty:
        recent_low = swing_lows["Low"].iloc[-1]

        if close < recent_low:
            bos = "BOS BAISSIER"

    return bos


# ============================================================
# SUPPORT / RÉSISTANCE
# ============================================================

def calculate_support_resistance(df, window=50):
    data = df.tail(window)

    if data.empty:
        return np.nan, np.nan

    support = data["Low"].min()
    resistance = data["High"].max()

    return support, resistance


# ============================================================
# FIBONACCI
# ============================================================

def calculate_fibonacci(df):
    """
    Calcule les principaux niveaux Fibonacci
    à partir du dernier swing significatif.
    """

    data = detect_swings(df)

    swing_highs = data[
        data["Swing_High"]
    ]

    swing_lows = data[
        data["Swing_Low"]
    ]

    if swing_highs.empty or swing_lows.empty:
        return {}

    last_high_idx = swing_highs.index[-1]
    last_low_idx = swing_lows.index[-1]

    high = swing_highs["High"].iloc[-1]
    low = swing_lows["Low"].iloc[-1]

    if high <= low:
        return {}

    levels = {}

    diff = high - low

    levels["23.6%"] = high - diff * 0.236
    levels["38.2%"] = high - diff * 0.382
    levels["50.0%"] = high - diff * 0.500
    levels["61.8%"] = high - diff * 0.618
    levels["78.6%"] = high - diff * 0.786

    levels["127.2%"] = high + diff * 0.272
    levels["161.8%"] = high + diff * 0.618

    levels["_high"] = high
    levels["_low"] = low

    return levels


# ============================================================
# CALCUL DES INDICATEURS
# ============================================================

def add_indicators(df):
    data = df.copy()

    data["EMA20"] = ema(
        data["Close"],
        20
    )

    data["EMA50"] = ema(
        data["Close"],
        50
    )

    data["SMA200"] = sma(
        data["Close"],
        200
    )

    data["RSI"] = calculate_rsi(
        data["Close"],
        14
    )

    (
        data["MACD"],
        data["MACD_Signal"],
        data["MACD_Hist"]
    ) = calculate_macd(
        data["Close"]
    )

    (
        data["ADX"],
        data["DI_Plus"],
        data["DI_Minus"]
    ) = calculate_adx(
        data,
        14
    )

    data["ATR"] = calculate_atr(
        data,
        14
    )

    (
        data["BB_Middle"],
        data["BB_Upper"],
        data["BB_Lower"]
    ) = calculate_bollinger(
        data["Close"],
        20,
        2
    )

    (
        data["Stoch_K"],
        data["Stoch_D"]
    ) = calculate_stochastic(
        data,
        14,
        3
    )

    return data


# ============================================================
# ANALYSE D'UN TIMEFRAME
# ============================================================

def analyze_timeframe(df):
    if df.empty:
        return None

    data = add_indicators(df)

    if len(data) < 30:
        return None

    (
        structure_data,
        high_labels,
        low_labels,
        structure
    ) = classify_structure(data)

    bos = detect_bos(data)

    support, resistance = calculate_support_resistance(
        data,
        50
    )

    fibonacci = calculate_fibonacci(data)

    last = data.iloc[-1]

    price = float(last["Close"])

    score = 0
    reasons = []

    # --------------------------------------------------------
    # EMA20 / EMA50
    # --------------------------------------------------------

    if pd.notna(last["EMA20"]) and pd.notna(last["EMA50"]):

        if last["EMA20"] > last["EMA50"]:
            score += 1
            reasons.append("EMA20 > EMA50")

        elif last["EMA20"] < last["EMA50"]:
            score -= 1
            reasons.append("EMA20 < EMA50")

    # --------------------------------------------------------
    # SMA200
    # --------------------------------------------------------

    if pd.notna(last["SMA200"]):

        if price > last["SMA200"]:
            score += 1
            reasons.append("Prix au-dessus SMA200")

        elif price < last["SMA200"]:
            score -= 1
            reasons.append("Prix sous SMA200")

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    if pd.notna(last["RSI"]):

        rsi = float(last["RSI"])

        if 50 <= rsi <= 70:
            score += 1
            reasons.append("RSI favorable aux acheteurs")

        elif 30 <= rsi < 50:
            score -= 1
            reasons.append("RSI favorable aux vendeurs")

        elif rsi > 70:
            reasons.append("RSI en zone élevée")

        elif rsi < 30:
            reasons.append("RSI en zone basse")

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    if (
        pd.notna(last["MACD"])
        and pd.notna(last["MACD_Signal"])
    ):

        if last["MACD"] > last["MACD_Signal"]:
            score += 1
            reasons.append("MACD haussier")

        elif last["MACD"] < last["MACD_Signal"]:
            score -= 1
            reasons.append("MACD baissier")

    # --------------------------------------------------------
    # ADX
    # --------------------------------------------------------

    if pd.notna(last["ADX"]):

        adx = float(last["ADX"])

        if adx >= 25:
            reasons.append("ADX confirme une tendance")

            if (
                pd.notna(last["DI_Plus"])
                and pd.notna(last["DI_Minus"])
            ):

                if last["DI_Plus"] > last["DI_Minus"]:
                    score += 1
                    reasons.append("DI+ > DI-")

                elif last["DI_Minus"] > last["DI_Plus"]:
                    score -= 1
                    reasons.append("DI- > DI+")

        else:
            reasons.append("ADX faible : marché potentiellement en range")

    # --------------------------------------------------------
    # STOCHASTIC
    # --------------------------------------------------------

    if (
        pd.notna(last["Stoch_K"])
        and pd.notna(last["Stoch_D"])
    ):

        if (
            last["Stoch_K"] > last["Stoch_D"]
            and last["Stoch_K"] < 80
        ):
            score += 1
            reasons.append("Stochastic haussier")

        elif (
            last["Stoch_K"] < last["Stoch_D"]
            and last["Stoch_K"] > 20
        ):
            score -= 1
            reasons.append("Stochastic baissier")

    # --------------------------------------------------------
    # STRUCTURE
    # --------------------------------------------------------

    if structure == "HAUSSIÈRE":
        score += 2
        reasons.append("Structure haussière")

    elif structure == "BAISSIÈRE":
        score -= 2
        reasons.append("Structure baissière")

    # --------------------------------------------------------
    # BOS
    # --------------------------------------------------------

    if bos == "BOS HAUSSIER":
        score += 2
        reasons.append("BOS haussier potentiel")

    elif bos == "BOS BAISSIER":
        score -= 2
        reasons.append("BOS baissier potentiel")

    # --------------------------------------------------------
    # BANDES DE BOLLINGER
    # --------------------------------------------------------

    if (
        pd.notna(last["BB_Upper"])
        and pd.notna(last["BB_Lower"])
    ):

        if price > last["BB_Middle"]:
            score += 0.5

        elif price < last["BB_Middle"]:
            score -= 0.5

    # --------------------------------------------------------
    # DIRECTION
    # --------------------------------------------------------

    if score >= 4:
        direction = "ACHAT"

    elif score <= -4:
        direction = "VENTE"

    else:
        direction = "NEUTRE"

        return {
        "data": data,
        "price": price,
        "score": score,
        "direction": direction,
    }
# ============================================================
# FOREX AI ANALYST
# indicators.py
# Calcul des indicateurs techniques
# ============================================================

import numpy as np
import pandas as pd


# ============================================================
# EMA
# ============================================================

def calculate_ema(
    data: pd.DataFrame,
    period: int
) -> pd.Series:
    """Calcule une moyenne mobile exponentielle."""

    return data["Close"].ewm(
        span=period,
        adjust=False
    ).mean()


# ============================================================
# SMA
# ============================================================

def calculate_sma(
    data: pd.DataFrame,
    period: int
) -> pd.Series:
    """Calcule une moyenne mobile simple."""

    return data["Close"].rolling(
        window=period
    ).mean()


# ============================================================
# RSI
# ============================================================

def calculate_rsi(
    data: pd.DataFrame,
    period: int = 14
) -> pd.Series:
    """Calcule le RSI."""

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = average_gain / average_loss.replace(
        0,
        np.nan
    )

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


# ============================================================
# MACD
# ============================================================

def calculate_macd(
    data: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> pd.DataFrame:
    """Calcule MACD, ligne signal et histogramme."""

    ema_fast = data["Close"].ewm(
        span=fast,
        adjust=False
    ).mean()

    ema_slow = data["Close"].ewm(
        span=slow,
        adjust=False
    ).mean()

    macd = ema_fast - ema_slow

    signal_line = macd.ewm(
        span=signal,
        adjust=False
    ).mean()

    histogram = macd - signal_line

    result = pd.DataFrame(
        index=data.index
    )

    result["MACD"] = macd
    result["MACD_Signal"] = signal_line
    result["MACD_Hist"] = histogram

    return result


# ============================================================
# TRUE RANGE
# ============================================================

def calculate_true_range(
    data: pd.DataFrame
) -> pd.Series:
    """Calcule le True Range."""

    previous_close = data["Close"].shift(1)

    range_1 = data["High"] - data["Low"]

    range_2 = (
        data["High"] - previous_close
    ).abs()

    range_3 = (
        data["Low"] - previous_close
    ).abs()

    true_range = pd.concat(
        [
            range_1,
            range_2,
            range_3,
        ],
        axis=1
    ).max(axis=1)

    return true_range


# ============================================================
# ATR
# ============================================================

def calculate_atr(
    data: pd.DataFrame,
    period: int = 14
) -> pd.Series:
    """Calcule l'Average True Range."""

    true_range = calculate_true_range(data)

    atr = true_range.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    return atr


# ============================================================
# ADX
# ============================================================

def calculate_adx(
    data: pd.DataFrame,
    period: int = 14
) -> pd.DataFrame:
    """Calcule l'ADX ainsi que +DI et -DI."""

    high = data["High"]
    low = data["Low"]

    previous_high = high.shift(1)
    previous_low = low.shift(1)

    up_move = high - previous_high
    down_move = previous_low - low

    plus_dm = pd.Series(
        np.where(
            (up_move > down_move) & (up_move > 0),
            up_move,
            0.0
        ),
        index=data.index
    )

    minus_dm = pd.Series(
        np.where(
            (down_move > up_move) & (down_move > 0),
            down_move,
            0.0
        ),
        index=data.index
    )

    true_range = calculate_true_range(data)

    atr = true_range.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    plus_di = (
        100
        * plus_dm.ewm(
            alpha=1 / period,
            adjust=False
        ).mean()
        / atr.replace(0, np.nan)
    )

    minus_di = (
        100
        * minus_dm.ewm(
            alpha=1 / period,
            adjust=False
        ).mean()
        / atr.replace(0, np.nan)
    )

    di_sum = (
        plus_di + minus_di
    ).replace(0, np.nan)

    dx = (
        100
        * (plus_di - minus_di).abs()
        / di_sum
    )

    adx = dx.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    result = pd.DataFrame(
        index=data.index
    )

    result["ADX"] = adx
    result["DI_Plus"] = plus_di
    result["DI_Minus"] = minus_di

    return result


# ============================================================
# BOLLINGER BANDS
# ============================================================

def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_multiplier: float = 2
) -> pd.DataFrame:
    """Calcule les bandes de Bollinger."""

    middle = data["Close"].rolling(
        window=period
    ).mean()

    standard_deviation = data["Close"].rolling(
        window=period
    ).std()

    upper = (
        middle
        + std_multiplier * standard_deviation
    )

    lower = (
        middle
        - std_multiplier * standard_deviation
    )

    result = pd.DataFrame(
        index=data.index
    )

    result["BB_Upper"] = upper
    result["BB_Middle"] = middle
    result["BB_Lower"] = lower

    return result


# ============================================================
# STOCHASTIC
# ============================================================

def calculate_stochastic(
    data: pd.DataFrame,
    k_period: int = 14,
    d_period: int = 3
) -> pd.DataFrame:
    """Calcule le Stochastic %K et %D."""

    lowest_low = data["Low"].rolling(
        window=k_period
    ).min()

    highest_high = data["High"].rolling(
        window=k_period
    ).max()

    denominator = (
        highest_high - lowest_low
    ).replace(0, np.nan)

    k = (
        100
        * (data["Close"] - lowest_low)
        / denominator
    )

    d = k.rolling(
        window=d_period
    ).mean()

    result = pd.DataFrame(
        index=data.index
    )

    result["Stoch_K"] = k
    result["Stoch_D"] = d

    return result


# ============================================================
# TOUS LES INDICATEURS
# ============================================================

def add_all_indicators(
    data: pd.DataFrame
) -> pd.DataFrame:
    """
    Ajoute tous les indicateurs techniques
    au DataFrame.
    """

    if data is None or data.empty:
        return pd.DataFrame()

    result = data.copy()

    # --------------------------------------------------------
    # Moyennes mobiles
    # --------------------------------------------------------

    result["EMA20"] = calculate_ema(
        result,
        20
    )

    result["EMA50"] = calculate_ema(
        result,
        50
    )

    result["SMA200"] = calculate_sma(
        result,
        200
    )

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    result["RSI"] = calculate_rsi(
        result,
        14
    )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    macd = calculate_macd(
        result,
        fast=12,
        slow=26,
        signal=9
    )

    result = result.join(
        macd
    )

    # --------------------------------------------------------
    # ATR
    # --------------------------------------------------------

    result["ATR"] = calculate_atr(
        result,
        14
    )

    # --------------------------------------------------------
    # ADX
    # --------------------------------------------------------

    adx = calculate_adx(
        result,
        14
    )

    result = result.join(
        adx
    )

    # --------------------------------------------------------
    # Bollinger Bands
    # --------------------------------------------------------

    bollinger = calculate_bollinger_bands(
        result,
        period=20,
        std_multiplier=2
    )

    result = result.join(
        bollinger
    )

    # --------------------------------------------------------
    # Stochastic
    # --------------------------------------------------------

    stochastic = calculate_stochastic(
        result,
        k_period=14,
        d_period=3
    )

    result = result.join(
        stochastic
    )

    return result
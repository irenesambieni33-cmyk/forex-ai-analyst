# ============================================================
# FOREX AI ANALYST
# structure.py
# Analyse de la structure du marché
# ============================================================

import numpy as np
import pandas as pd


# ============================================================
# DÉTECTION DES SWINGS
# ============================================================

def detect_swings(
    data: pd.DataFrame,
    lookback: int = 3
) -> pd.DataFrame:
    """
    Détecte les Swing High et Swing Low.

    Un Swing High est un sommet supérieur aux sommets
    des bougies voisines.

    Un Swing Low est un creux inférieur aux creux
    des bougies voisines.
    """

    if data is None or data.empty:
        return pd.DataFrame()

    result = data.copy()

    result["Swing_High"] = np.nan
    result["Swing_Low"] = np.nan

    highs = result["High"]
    lows = result["Low"]

    for i in range(
        lookback,
        len(result) - lookback
    ):

        current_high = highs.iloc[i]
        current_low = lows.iloc[i]

        left_highs = highs.iloc[
            i - lookback:i
        ]

        right_highs = highs.iloc[
            i + 1:i + lookback + 1
        ]

        left_lows = lows.iloc[
            i - lookback:i
        ]

        right_lows = lows.iloc[
            i + 1:i + lookback + 1
        ]

        # ----------------------------------------------------
        # Swing High
        # ----------------------------------------------------

        if (
            current_high > left_highs.max()
            and current_high > right_highs.max()
        ):
            result.iloc[
                i,
                result.columns.get_loc("Swing_High")
            ] = current_high

        # ----------------------------------------------------
        # Swing Low
        # ----------------------------------------------------

        if (
            current_low < left_lows.min()
            and current_low < right_lows.min()
        ):
            result.iloc[
                i,
                result.columns.get_loc("Swing_Low")
            ] = current_low

    return result


# ============================================================
# CLASSIFICATION DES SWINGS
# ============================================================

def classify_swings(
    data: pd.DataFrame
) -> pd.DataFrame:
    """
    Classe les swings en :

    HH = Higher High
    HL = Higher Low
    LH = Lower High
    LL = Lower Low
    """

    if data is None or data.empty:
        return pd.DataFrame()

    result = data.copy()

    result["Swing_Type"] = None

    previous_high = None
    previous_low = None

    for i in range(len(result)):

        swing_high = result["Swing_High"].iloc[i]
        swing_low = result["Swing_Low"].iloc[i]

        # ----------------------------------------------------
        # Classification des sommets
        # ----------------------------------------------------

        if pd.notna(swing_high):

            if previous_high is not None:

                if swing_high > previous_high:
                    result.iloc[
                        i,
                        result.columns.get_loc("Swing_Type")
                    ] = "HH"

                elif swing_high < previous_high:
                    result.iloc[
                        i,
                        result.columns.get_loc("Swing_Type")
                    ] = "LH"

            previous_high = swing_high

        # ----------------------------------------------------
        # Classification des creux
        # ----------------------------------------------------

        if pd.notna(swing_low):

            if previous_low is not None:

                if swing_low > previous_low:
                    result.iloc[
                        i,
                        result.columns.get_loc("Swing_Type")
                    ] = "HL"

                elif swing_low < previous_low:
                    result.iloc[
                        i,
                        result.columns.get_loc("Swing_Type")
                    ] = "LL"

            previous_low = swing_low

    return result


# ============================================================
# DÉTECTION DU BOS
# ============================================================

def detect_bos(
    data: pd.DataFrame
) -> pd.DataFrame:
    """
    Détecte les Break of Structure (BOS).

    BOS haussier :
        le prix casse un précédent Swing High.

    BOS baissier :
        le prix casse un précédent Swing Low.
    """

    if data is None or data.empty:
        return pd.DataFrame()

    result = data.copy()

    result["BOS"] = None

    last_swing_high = None
    last_swing_low = None

    high_already_broken = False
    low_already_broken = False

    for i in range(len(result)):

        close = result["Close"].iloc[i]

        swing_high = result["Swing_High"].iloc[i]
        swing_low = result["Swing_Low"].iloc[i]

        # ----------------------------------------------------
        # Mise à jour du dernier Swing High
        # ----------------------------------------------------

        if pd.notna(swing_high):

            last_swing_high = swing_high
            high_already_broken = False

        # ----------------------------------------------------
        # Mise à jour du dernier Swing Low
        # ----------------------------------------------------

        if pd.notna(swing_low):

            last_swing_low = swing_low
            low_already_broken = False

        # ----------------------------------------------------
        # BOS haussier
        # ----------------------------------------------------

        if (
            last_swing_high is not None
            and close > last_swing_high
            and not high_already_broken
        ):

            result.iloc[
                i,
                result.columns.get_loc("BOS")
            ] = "BULLISH_BOS"

            high_already_broken = True

        # ----------------------------------------------------
        # BOS baissier
        # ----------------------------------------------------

        elif (
            last_swing_low is not None
            and close < last_swing_low
            and not low_already_broken
        ):

            result.iloc[
                i,
                result.columns.get_loc("BOS")
            ] = "BEARISH_BOS"

            low_already_broken = True

    return result


# ============================================================
# TENDANCE À PARTIR DE LA STRUCTURE
# ============================================================

def determine_structure_trend(
    data: pd.DataFrame
) -> str:
    """
    Détermine une tendance structurelle simple.

    Retourne :
        HAUSSIÈRE
        BAISSIÈRE
        NEUTRE
    """

    if data is None or data.empty:
        return "NEUTRE"

    swing_types = (
        data["Swing_Type"]
        .dropna()
        .tolist()
    )

    if len(swing_types) < 2:
        return "NEUTRE"

    recent_types = swing_types[-6:]

    bullish_points = sum(
        1
        for value in recent_types
        if value in ["HH", "HL"]
    )

    bearish_points = sum(
        1
        for value in recent_types
        if value in ["LH", "LL"]
    )

    if bullish_points > bearish_points:
        return "HAUSSIÈRE"

    if bearish_points > bullish_points:
        return "BAISSIÈRE"

    return "NEUTRE"


# ============================================================
# ANALYSE COMPLÈTE DE LA STRUCTURE
# ============================================================

def analyze_market_structure(
    data: pd.DataFrame,
    lookback: int = 3
) -> dict:
    """
    Effectue l'analyse complète de la structure.
    """

    if data is None or data.empty:
        return {
            "data": pd.DataFrame(),
            "trend": "NEUTRE",
            "last_swing_high": None,
            "last_swing_low": None,
            "last_swing_type": None,
            "last_bos": None,
        }

    result = detect_swings(
        data,
        lookback=lookback
    )

    result = classify_swings(
        result
    )

    result = detect_bos(
        result
    )

    # --------------------------------------------------------
    # Dernier Swing High
    # --------------------------------------------------------

    swing_highs = result[
        "Swing_High"
    ].dropna()

    last_swing_high = (
        float(swing_highs.iloc[-1])
        if not swing_highs.empty
        else None
    )

    # --------------------------------------------------------
    # Dernier Swing Low
    # --------------------------------------------------------

    swing_lows = result[
        "Swing_Low"
    ].dropna()

    last_swing_low = (
        float(swing_lows.iloc[-1])
        if not swing_lows.empty
        else None
    )

    # --------------------------------------------------------
    # Dernier type de structure
    # --------------------------------------------------------

    swing_types = result[
        "Swing_Type"
    ].dropna()

    last_swing_type = (
        swing_types.iloc[-1]
        if not swing_types.empty
        else None
    )

    # --------------------------------------------------------
    # Dernier BOS
    # --------------------------------------------------------

    bos_values = result[
        "BOS"
    ].dropna()

    last_bos = (
        bos_values.iloc[-1]
        if not bos_values.empty
        else None
    )

    trend = determine_structure_trend(
        result
    )

    return {
        "data": result,
        "trend": trend,
        "last_swing_high": last_swing_high,
        "last_swing_low": last_swing_low,
        "last_swing_type": last_swing_type,
        "last_bos": last_bos,
    }
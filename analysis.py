# ============================================================
# FOREX AI ANALYST
# analysis.py
# Moteur d'analyse technique
# ============================================================

import pandas as pd
import numpy as np

from config import (
    TIMEFRAMES,
    TIMEFRAME_ORDER,
    INDICATOR_SETTINGS,
    DECISION_SETTINGS,
    STRUCTURE_SETTINGS,
)

from data import load_timeframe_data, get_last_price

from indicators import add_all_indicators

from structure import analyze_market_structure

from fibonacci import analyze_fibonacci


# ============================================================
# SCORE D'UN TIMEFRAME
# ============================================================

def calculate_timeframe_score(
    data: pd.DataFrame
) -> dict:
    """
    Calcule le score technique d'un timeframe.

    Le score combine :
    - EMA20 / EMA50
    - SMA200
    - RSI
    - MACD
    - ADX
    - Stochastic
    - Bollinger Bands
    - structure du marché
    """

    if data is None or data.empty:
        return {
            "score": 0.0,
            "direction": "NEUTRE",
            "reasons": [],
        }

    last = data.iloc[-1]

    score = 0.0
    reasons = []

    # ========================================================
    # EMA20 / EMA50
    # ========================================================

    ema20 = last.get("EMA20")
    ema50 = last.get("EMA50")

    if pd.notna(ema20) and pd.notna(ema50):

        if ema20 > ema50:
            score += 1.0
            reasons.append(
                "EMA20 au-dessus de EMA50 : biais haussier."
            )

        elif ema20 < ema50:
            score -= 1.0
            reasons.append(
                "EMA20 sous EMA50 : biais baissier."
            )

    # ========================================================
    # SMA200
    # ========================================================

    sma200 = last.get("SMA200")
    close = last.get("Close")

    if pd.notna(sma200) and pd.notna(close):

        if close > sma200:
            score += 1.0
            reasons.append(
                "Prix au-dessus de SMA200."
            )

        elif close < sma200:
            score -= 1.0
            reasons.append(
                "Prix sous SMA200."
            )

    # ========================================================
    # RSI
    # ========================================================

    rsi = last.get("RSI")

    if pd.notna(rsi):

        if rsi >= 55 and rsi < 70:
            score += 1.0
            reasons.append(
                f"RSI {rsi:.1f} : momentum haussier."
            )

        elif rsi <= 45 and rsi > 30:
            score -= 1.0
            reasons.append(
                f"RSI {rsi:.1f} : momentum baissier."
            )

        elif rsi >= 70:
            reasons.append(
                f"RSI {rsi:.1f} : zone de surachat."
            )

        elif rsi <= 30:
            reasons.append(
                f"RSI {rsi:.1f} : zone de survente."
            )

    # ========================================================
    # MACD
    # ========================================================

    macd = last.get("MACD")
    macd_signal = last.get("MACD_Signal")

    if (
        pd.notna(macd)
        and pd.notna(macd_signal)
    ):

        if macd > macd_signal:
            score += 1.0
            reasons.append(
                "MACD supérieur à sa ligne signal."
            )

        elif macd < macd_signal:
            score -= 1.0
            reasons.append(
                "MACD inférieur à sa ligne signal."
            )

    # ========================================================
    # ADX + DI
    # ========================================================

    adx = last.get("ADX")
    di_plus = last.get("DI_Plus")
    di_minus = last.get("DI_Minus")

    if (
        pd.notna(adx)
        and pd.notna(di_plus)
        and pd.notna(di_minus)
    ):

        if adx >= 20:

            if di_plus > di_minus:
                score += 1.0
                reasons.append(
                    f"ADX {adx:.1f} avec DI+ dominant."
                )

            elif di_minus > di_plus:
                score -= 1.0
                reasons.append(
                    f"ADX {adx:.1f} avec DI- dominant."
                )

        else:
            reasons.append(
                f"ADX {adx:.1f} : tendance peu affirmée."
            )

    # ========================================================
    # STOCHASTIC
    # ========================================================

    stoch_k = last.get("Stoch_K")
    stoch_d = last.get("Stoch_D")

    if (
        pd.notna(stoch_k)
        and pd.notna(stoch_d)
    ):

        if (
            stoch_k > stoch_d
            and stoch_k < 80
        ):
            score += 0.5
            reasons.append(
                "Stochastic favorable aux acheteurs."
            )

        elif (
            stoch_k < stoch_d
            and stoch_k > 20
        ):
            score -= 0.5
            reasons.append(
                "Stochastic favorable aux vendeurs."
            )

    # ========================================================
    # BOLLINGER BANDS
    # ========================================================

    bb_middle = last.get("BB_Middle")

    if (
        pd.notna(bb_middle)
        and pd.notna(close)
    ):

        if close > bb_middle:
            score += 0.5
            reasons.append(
                "Prix au-dessus de la moyenne de Bollinger."
            )

        elif close < bb_middle:
            score -= 0.5
            reasons.append(
                "Prix sous la moyenne de Bollinger."
            )

    # ========================================================
    # DIRECTION
    # ========================================================

    if score >= 2.0:
        direction = "ACHAT"

    elif score <= -2.0:
        direction = "VENTE"

    else:
        direction = "NEUTRE"

    return {
        "score": round(score, 2),
        "direction": direction,
        "reasons": reasons,
    }


# ============================================================
# SCORE DE STRUCTURE
# ============================================================

def calculate_structure_score(
    structure: dict
) -> tuple:
    """
    Convertit la structure du marché en score.
    """

    if not structure:
        return 0.0, []

    score = 0.0
    reasons = []

    trend = structure.get(
        "trend",
        "NEUTRE"
    )

    last_bos = structure.get(
        "last_bos"
    )

    last_swing_type = structure.get(
        "last_swing_type"
    )

    # --------------------------------------------------------
    # Tendance structurelle
    # --------------------------------------------------------

    if trend == "HAUSSIÈRE":

        score += 1.5

        reasons.append(
            "Structure du marché haussière."
        )

    elif trend == "BAISSIÈRE":

        score -= 1.5

        reasons.append(
            "Structure du marché baissière."
        )

    # --------------------------------------------------------
    # BOS
    # --------------------------------------------------------

    if last_bos == "BULLISH_BOS":

        score += 1.5

        reasons.append(
            "Dernier BOS haussier détecté."
        )

    elif last_bos == "BEARISH_BOS":

        score -= 1.5

        reasons.append(
            "Dernier BOS baissier détecté."
        )

    # --------------------------------------------------------
    # Dernier swing
    # --------------------------------------------------------

    if last_swing_type in ["HH", "HL"]:

        score += 0.5

        reasons.append(
            f"Dernière structure : {last_swing_type}."
        )

    elif last_swing_type in ["LH", "LL"]:

        score -= 0.5

        reasons.append(
            f"Dernière structure : {last_swing_type}."
        )

    return round(score, 2), reasons


# ============================================================
# ANALYSE D'UN TIMEFRAME
# ============================================================

def analyze_single_timeframe(
    ticker: str,
    timeframe: str
) -> dict:
    """
    Analyse complètement un timeframe.
    """

    data = load_timeframe_data(
        ticker=ticker,
        timeframe=timeframe,
    )

    if data.empty:
        return {
            "timeframe": timeframe,
            "data": pd.DataFrame(),
            "price": None,
            "score": 0.0,
            "direction": "NEUTRE",
            "structure": {},
            "fibonacci": {},
            "reasons": [
                "Données indisponibles."
            ],
        }

    # --------------------------------------------------------
    # Indicateurs
    # --------------------------------------------------------

    data = add_all_indicators(
        data
    )

    # --------------------------------------------------------
    # Structure
    # --------------------------------------------------------

    structure = analyze_market_structure(
        data,
        lookback=STRUCTURE_SETTINGS[
            "SWING_LOOKBACK"
        ],
    )

    structure_data = structure.get(
        "data"
    )

    if (
        structure_data is not None
        and not structure_data.empty
    ):
        data = structure_data

    # --------------------------------------------------------
    # Score indicateurs
    # --------------------------------------------------------

    indicator_result = calculate_timeframe_score(
        data
    )

    indicator_score = indicator_result[
        "score"
    ]

    reasons = indicator_result[
        "reasons"
    ].copy()

    # --------------------------------------------------------
    # Score structure
    # --------------------------------------------------------

    structure_score, structure_reasons = (
        calculate_structure_score(
            structure
        )
    )

    score = (
        indicator_score
        + structure_score
    )

    reasons.extend(
        structure_reasons
    )

    # --------------------------------------------------------
    # Direction finale du timeframe
    # --------------------------------------------------------

    if score >= 3.0:
        direction = "ACHAT"

    elif score <= -3.0:
        direction = "VENTE"

    else:
        direction = "NEUTRE"

    # --------------------------------------------------------
    # Fibonacci
    # --------------------------------------------------------

    current_price = get_last_price(
        data
    )

    fibonacci = analyze_fibonacci(
        swing_high=structure.get(
            "last_swing_high"
        ),
        swing_low=structure.get(
            "last_swing_low"
        ),
        direction=(
            "HAUSSIÈRE"
            if direction == "ACHAT"
            else "BAISSIÈRE"
            if direction == "VENTE"
            else "NEUTRE"
        ),
        current_price=current_price,
    )

    return {
        "timeframe": timeframe,
        "data": data,
        "price": current_price,
        "score": round(score, 2),
        "direction": direction,
        "indicator_score": round(
            indicator_score,
            2
        ),
        "structure_score": round(
            structure_score,
            2
        ),
        "structure": structure,
        "fibonacci": fibonacci,
        "reasons": reasons,
    }


# ============================================================
# ANALYSE MULTI-TIMEFRAME
# ============================================================

def analyze_all_timeframes(
    ticker: str
) -> dict:
    """
    Analyse :

    D1 → H4 → H1 → M15 → M5

    avec les pondérations définies
    dans config.py.
    """

    results = {}

    weighted_score = 0.0
    total_weight = 0.0

    all_reasons = []

    for timeframe in TIMEFRAME_ORDER:

        result = analyze_single_timeframe(
            ticker=ticker,
            timeframe=timeframe,
        )

        results[timeframe] = result

        weight = TIMEFRAMES[
            timeframe
        ]["weight"]

        score = result[
            "score"
        ]

        # ----------------------------------------------------
        # Score pondéré
        # ----------------------------------------------------

        weighted_score += (
            score * weight
        )

        total_weight += weight

        # ----------------------------------------------------
        # Raisons
        # ----------------------------------------------------

        for reason in result.get(
            "reasons",
            []
        ):

            all_reasons.append(
                f"{timeframe} : {reason}"
            )

    # ========================================================
    # SCORE GLOBAL
    # ========================================================

    if total_weight > 0:

        global_score = (
            weighted_score
            / total_weight
        )

    else:

        global_score = 0.0

    global_score = round(
        global_score,
        2
    )

    # ========================================================
    # DIRECTION GLOBALE
    # ========================================================

    buy_threshold = DECISION_SETTINGS[
        "BUY_THRESHOLD"
    ]

    sell_threshold = DECISION_SETTINGS[
        "SELL_THRESHOLD"
    ]

    if global_score >= buy_threshold:

        decision = "ACHAT"

    elif global_score <= sell_threshold:

        decision = "VENTE"

    else:

        decision = "ATTENDRE"

    # ========================================================
    # ALIGNEMENT DES TIMEFRAMES
    # ========================================================

    directions = {
        timeframe: results[timeframe][
            "direction"
        ]
        for timeframe in TIMEFRAME_ORDER
        if results[timeframe]["data"] is not None
        and not results[timeframe]["data"].empty
    }

    bullish_count = sum(
        1
        for direction in directions.values()
        if direction == "ACHAT"
    )

    bearish_count = sum(
        1
        for direction in directions.values()
        if direction == "VENTE"
    )

    neutral_count = sum(
        1
        for direction in directions.values()
        if direction == "NEUTRE"
    )

    # ========================================================
    # CONFLUENCE
    # ========================================================

    confluence = {
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "neutral_count": neutral_count,
        "total_timeframes": len(directions),
    }

    # ========================================================
    # CONFIANCE
    # ========================================================

    total_timeframes = len(
        directions
    )

    if total_timeframes == 0:

        confidence = 0.0

    else:

        dominant_count = max(
            bullish_count,
            bearish_count
        )

        confidence = (
            dominant_count
            / total_timeframes
        ) * 100

    confidence = round(
        confidence,
        1
    )

    return {
        "timeframes": results,
        "global_score": global_score,
        "decision": decision,
        "confidence": confidence,
        "confluence": confluence,
        "reasons": all_reasons,
    }


# ============================================================
# RÉSUMÉ DE L'ANALYSE
# ============================================================

def build_analysis_summary(
    analysis: dict
) -> str:
    """
    Génère une explication simple de la décision.
    """

    if not analysis:
        return "Analyse indisponible."

    decision = analysis.get(
        "decision",
        "ATTENDRE"
    )

    score = analysis.get(
        "global_score",
        0.0
    )

    confidence = analysis.get(
        "confidence",
        0.0
    )

    confluence = analysis.get(
        "confluence",
        {}
    )

    bullish = confluence.get(
        "bullish_count",
        0
    )

    bearish = confluence.get(
        "bearish_count",
        0
    )

    neutral = confluence.get(
        "neutral_count",
        0
    )

    if decision == "ACHAT":

        return (
            f"Biais haussier détecté. "
            f"Score global : {score:.2f}. "
            f"Confiance : {confidence:.1f}%. "
            f"{bullish} timeframe(s) haussier(s), "
            f"{bearish} baissier(s) et "
            f"{neutral} neutre(s)."
        )

    if decision == "VENTE":

        return (
            f"Biais baissier détecté. "
            f"Score global : {score:.2f}. "
            f"Confiance : {confidence:.1f}%. "
            f"{bearish} timeframe(s) baissier(s), "
            f"{bullish} haussier(s) et "
            f"{neutral} neutre(s)."
        )

    return (
        f"Les conditions ne sont pas suffisamment "
        f"alignées pour une décision. "
        f"Score global : {score:.2f}. "
        f"Confiance : {confidence:.1f}%. "
        f"Décision : ATTENDRE."
    )
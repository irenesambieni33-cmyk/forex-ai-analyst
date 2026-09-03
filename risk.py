# ============================================================
# FOREX AI ANALYST
# risk.py
# Gestion du risque et calcul des niveaux
# ============================================================

import math

from config import RISK_SETTINGS


# ============================================================
# ARRONDI DU PRIX
# ============================================================

def round_price(
    price: float,
    decimals: int = 5
) -> float:
    """Arrondit proprement un prix."""

    if price is None:
        return None

    return round(
        float(price),
        decimals
    )


# ============================================================
# CALCUL DU RISQUE / RENDEMENT
# ============================================================

def calculate_risk_reward(
    entry: float,
    stop_loss: float,
    take_profit: float
) -> float:
    """
    Calcule le ratio Risk/Reward.

    R:R = distance Entry → TP
          -------------------
          distance Entry → SL
    """

    if (
        entry is None
        or stop_loss is None
        or take_profit is None
    ):
        return 0.0

    risk = abs(
        entry - stop_loss
    )

    reward = abs(
        take_profit - entry
    )

    if risk <= 0:
        return 0.0

    return round(
        reward / risk,
        2
    )


# ============================================================
# VALIDATION DU R:R
# ============================================================

def is_valid_risk_reward(
    risk_reward: float
) -> bool:
    """
    Vérifie si le R:R respecte le minimum configuré.
    """

    minimum = RISK_SETTINGS[
        "MIN_RISK_REWARD"
    ]

    return (
        risk_reward >= minimum
    )


# ============================================================
# CALCUL DES NIVEAUX
# ============================================================

def calculate_trade_levels(
    entry: float,
    atr: float,
    direction: str
) -> dict:
    """
    Calcule Entry, SL, TP1 et TP2
    à partir de l'ATR.

    Achat :
        SL sous l'entrée
        TP au-dessus

    Vente :
        SL au-dessus de l'entrée
        TP en dessous
    """

    if (
        entry is None
        or atr is None
        or atr <= 0
    ):
        return {
            "entry": None,
            "stop_loss": None,
            "take_profit_1": None,
            "take_profit_2": None,
            "risk_reward_tp1": 0.0,
            "risk_reward_tp2": 0.0,
            "valid_tp1": False,
            "valid_tp2": False,
        }

    # --------------------------------------------------------
    # Distance du Stop Loss
    # --------------------------------------------------------

    stop_distance = atr * 1.5

    # --------------------------------------------------------
    # Achat
    # --------------------------------------------------------

    if direction == "ACHAT":

        stop_loss = (
            entry - stop_distance
        )

        take_profit_1 = (
            entry + stop_distance * 2
        )

        take_profit_2 = (
            entry + stop_distance * 3
        )

    # --------------------------------------------------------
    # Vente
    # --------------------------------------------------------

    elif direction == "VENTE":

        stop_loss = (
            entry + stop_distance
        )

        take_profit_1 = (
            entry - stop_distance * 2
        )

        take_profit_2 = (
            entry - stop_distance * 3
        )

    else:

        return {
            "entry": round_price(entry),
            "stop_loss": None,
            "take_profit_1": None,
            "take_profit_2": None,
            "risk_reward_tp1": 0.0,
            "risk_reward_tp2": 0.0,
            "valid_tp1": False,
            "valid_tp2": False,
        }

    # --------------------------------------------------------
    # R:R
    # --------------------------------------------------------

    risk_reward_tp1 = calculate_risk_reward(
        entry,
        stop_loss,
        take_profit_1
    )

    risk_reward_tp2 = calculate_risk_reward(
        entry,
        stop_loss,
        take_profit_2
    )

    return {
        "entry": round_price(entry),

        "stop_loss": round_price(
            stop_loss
        ),

        "take_profit_1": round_price(
            take_profit_1
        ),

        "take_profit_2": round_price(
            take_profit_2
        ),

        "risk_reward_tp1": risk_reward_tp1,

        "risk_reward_tp2": risk_reward_tp2,

        "valid_tp1": is_valid_risk_reward(
            risk_reward_tp1
        ),

        "valid_tp2": is_valid_risk_reward(
            risk_reward_tp2
        ),
    }


# ============================================================
# RISQUE FINANCIER
# ============================================================

def calculate_money_risk(
    capital: float
) -> float:
    """
    Calcule le montant maximal théorique
    risqué sur une position.
    """

    if capital is None or capital <= 0:
        return 0.0

    risk_percentage = RISK_SETTINGS[
        "RISK_PER_TRADE"
    ]

    return round(
        capital * risk_percentage,
        2
    )


# ============================================================
# RISQUE CUMULÉ
# ============================================================

def calculate_max_total_risk(
    capital: float
) -> float:
    """
    Calcule le montant maximal théorique
    de risque cumulé.
    """

    if capital is None or capital <= 0:
        return 0.0

    max_risk = RISK_SETTINGS[
        "MAX_TOTAL_RISK"
    ]

    return round(
        capital * max_risk,
        2
    )


# ============================================================
# TAILLE DE POSITION THÉORIQUE
# ============================================================

def calculate_position_size(
    capital: float,
    entry: float,
    stop_loss: float,
    risk_percentage: float = None
) -> float:
    """
    Calcule une taille de position théorique.

    Cette fonction ne transmet aucun ordre
    à un broker.
    """

    if (
        capital is None
        or capital <= 0
        or entry is None
        or stop_loss is None
    ):
        return 0.0

    distance = abs(
        entry - stop_loss
    )

    if distance <= 0:
        return 0.0

    if risk_percentage is None:

        risk_percentage = RISK_SETTINGS[
            "RISK_PER_TRADE"
        ]

    if (
        risk_percentage <= 0
        or risk_percentage > 1
    ):
        return 0.0

    money_at_risk = (
        capital
        * risk_percentage
    )

    position_size = (
        money_at_risk
        / distance
    )

    if not math.isfinite(
        position_size
    ):
        return 0.0

    return round(
        position_size,
        4
    )


# ============================================================
# ANALYSE COMPLÈTE DU RISQUE
# ============================================================

def analyze_risk(
    entry: float,
    atr: float,
    direction: str,
    capital: float = None
) -> dict:
    """
    Effectue l'analyse complète du risque.
    """

    levels = calculate_trade_levels(
        entry=entry,
        atr=atr,
        direction=direction,
    )

    result = {
        "levels": levels,

        "risk_per_trade_percent":
            RISK_SETTINGS[
                "RISK_PER_TRADE"
            ] * 100,

        "max_total_risk_percent":
            RISK_SETTINGS[
                "MAX_TOTAL_RISK"
            ] * 100,

        "min_risk_reward":
            RISK_SETTINGS[
                "MIN_RISK_REWARD"
            ],

        "money_risk": None,

        "max_total_money_risk": None,

        "position_size": None,

        "warning": (
            "Calculs théoriques uniquement. "
            "Aucun ordre automatique n'est envoyé."
        ),
    }

    if capital is not None:

        result[
            "money_risk"
        ] = calculate_money_risk(
            capital
        )

        result[
            "max_total_money_risk"
        ] = calculate_max_total_risk(
            capital
        )

        if (
            levels["entry"] is not None
            and levels["stop_loss"] is not None
        ):

            result[
                "position_size"
            ] = calculate_position_size(
                capital=capital,
                entry=levels["entry"],
                stop_loss=levels["stop_loss"],
            )

    return result
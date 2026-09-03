# ============================================================
# FOREX AI ANALYST
# fibonacci.py
# Analyse Fibonacci
# ============================================================

import pandas as pd

from config import FIBONACCI_LEVELS


# ============================================================
# CALCUL DES NIVEAUX DE FIBONACCI
# ============================================================

def calculate_fibonacci(
    swing_high: float,
    swing_low: float,
    direction: str
) -> dict:
    """
    Calcule les niveaux de Fibonacci à partir d'un
    Swing High et d'un Swing Low.

    direction :
        HAUSSIÈRE
        BAISSIÈRE
    """

    if swing_high is None or swing_low is None:
        return {}

    if swing_high <= swing_low:
        return {}

    difference = swing_high - swing_low

    levels = {}

    # --------------------------------------------------------
    # Mouvement haussier
    # --------------------------------------------------------

    if direction == "HAUSSIÈRE":

        for ratio in FIBONACCI_LEVELS:
            price = swing_high - (
                difference * ratio
            )

            levels[ratio] = float(price)

    # --------------------------------------------------------
    # Mouvement baissier
    # --------------------------------------------------------

    elif direction == "BAISSIÈRE":

        for ratio in FIBONACCI_LEVELS:
            price = swing_low + (
                difference * ratio
            )

            levels[ratio] = float(price)

    return levels


# ============================================================
# FORMATAGE DES NIVEAUX
# ============================================================

def format_fibonacci_levels(
    levels: dict
) -> pd.DataFrame:
    """
    Transforme les niveaux Fibonacci en DataFrame
    pour faciliter leur affichage dans l'interface.
    """

    if not levels:
        return pd.DataFrame(
            columns=[
                "Niveau",
                "Prix",
            ]
        )

    rows = []

    for ratio, price in levels.items():

        rows.append(
            {
                "Niveau": f"{ratio * 100:.1f}%",
                "Prix": price,
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# NIVEAU FIBONACCI LE PLUS PROCHE
# ============================================================

def find_nearest_fibonacci(
    price: float,
    levels: dict
) -> dict:
    """
    Trouve le niveau Fibonacci le plus proche
    du prix actuel.
    """

    if price is None or not levels:
        return {
            "ratio": None,
            "price": None,
            "distance": None,
        }

    nearest_ratio = min(
        levels,
        key=lambda ratio: abs(
            levels[ratio] - price
        )
    )

    nearest_price = levels[
        nearest_ratio
    ]

    distance = abs(
        nearest_price - price
    )

    return {
        "ratio": nearest_ratio,
        "price": float(nearest_price),
        "distance": float(distance),
    }


# ============================================================
# CONFLUENCE AVEC UN NIVEAU
# ============================================================

def fibonacci_confluence(
    price: float,
    levels: dict,
    tolerance: float
) -> dict:
    """
    Vérifie si le prix actuel se trouve
    suffisamment proche d'un niveau Fibonacci.
    """

    if (
        price is None
        or not levels
        or tolerance is None
        or tolerance <= 0
    ):
        return {
            "found": False,
            "ratio": None,
            "level": None,
            "distance": None,
        }

    nearest = find_nearest_fibonacci(
        price,
        levels
    )

    if nearest["price"] is None:
        return {
            "found": False,
            "ratio": None,
            "level": None,
            "distance": None,
        }

    found = (
        nearest["distance"] <= tolerance
    )

    return {
        "found": found,
        "ratio": nearest["ratio"],
        "level": nearest["price"],
        "distance": nearest["distance"],
    }


# ============================================================
# ANALYSE FIBONACCI COMPLÈTE
# ============================================================

def analyze_fibonacci(
    swing_high: float,
    swing_low: float,
    direction: str,
    current_price: float = None,
    tolerance: float = None
) -> dict:
    """
    Effectue l'analyse complète de Fibonacci.
    """

    levels = calculate_fibonacci(
        swing_high=swing_high,
        swing_low=swing_low,
        direction=direction,
    )

    result = {
        "levels": levels,
        "table": format_fibonacci_levels(
            levels
        ),
        "nearest": {
            "ratio": None,
            "price": None,
            "distance": None,
        },
        "confluence": {
            "found": False,
            "ratio": None,
            "level": None,
            "distance": None,
        },
    }

    if current_price is not None and levels:

        result["nearest"] = find_nearest_fibonacci(
            current_price,
            levels
        )

        if tolerance is not None:

            result["confluence"] = fibonacci_confluence(
                current_price,
                levels,
                tolerance
            )

    return result
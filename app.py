import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Forex AI Analyst V2",
    page_icon="📈",
    layout="wide"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.title {
    font-size: 2.5rem;
    font-weight: 800;
}

.subtitle {
    color: #777;
    margin-bottom: 25px;
}

.signal-buy {
    padding: 18px;
    border-radius: 12px;
    background-color: #d9f7e3;
    border: 1px solid #55b978;
    text-align: center;
    font-size: 30px;
    font-weight: 800;
}

.signal-sell {
    padding: 18px;
    border-radius: 12px;
    background-color: #ffe0e0;
    border: 1px solid #d85c5c;
    text-align: center;
    font-size: 30px;
    font-weight: 800;
}

.signal-wait {
    padding: 18px;
    border-radius: 12px;
    background-color: #fff1cc;
    border: 1px solid #d6a83d;
    text-align: center;
    font-size: 30px;
    font-weight: 800;
}

.signal-none {
    padding: 18px;
    border-radius: 12px;
    background-color: #eeeeee;
    border: 1px solid #999999;
    text-align: center;
    font-size: 30px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# TITRE
# ============================================================

st.markdown(
    '<div class="title">📈 Forex AI Analyst V2</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyse technique multi-timeframe avec confluence'
    '</div>',
    unsafe_allow_html=True
)

# ============================================================
# PARAMÈTRES
# ============================================================

col1, col2 = st.columns(2)

with col1:
    asset = st.selectbox(
        "Instrument",
        ["EUR/USD", "XAU/USD"]
    )

with col2:
    chart_tf = st.selectbox(
        "Timeframe du graphique",
        ["D1", "H4", "H1", "M15", "M5"]
    )

# ============================================================
# TICKERS
# ============================================================

ticker_map = {
    "EUR/USD": "EURUSD=X",
    "XAU/USD": "XAUUSD=X"
}

ticker = ticker_map[asset]

# ============================================================
# PARAMÈTRES DES TIMEFRAMES
# ============================================================

TIMEFRAMES = {
    "D1": {
        "interval": "1d",
        "period": "1y"
    },
    "H4": {
        "interval": "1h",
        "period": "3mo"
    },
    "H1": {
        "interval": "1h",
        "period": "3mo"
    },
    "M15": {
        "interval": "15m",
        "period": "1mo"
    },
    "M5": {
        "interval": "5m",
        "period": "5d"
    }
}

# ============================================================
# INDICATEURS
# ============================================================

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    return 100 - (100 / (1 + rs))


def calculate_macd(series):

    ema12 = series.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = series.ewm(
        span=26,
        adjust=False
    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    histogram = macd - signal

    return macd, signal, histogram


def calculate_atr(data, period=14):

    high_low = data["High"] - data["Low"]

    high_close = (
        data["High"] -
        data["Close"].shift()
    ).abs()

    low_close = (
        data["Low"] -
        data["Close"].shift()
    ).abs()

    true_range = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    ).max(axis=1)

    return true_range.rolling(period).mean()


def calculate_adx(data, period=14):

    high = data["High"]
    low = data["Low"]
    close = data["Close"]

    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = np.where(
        (up_move > down_move) & (up_move > 0),
        up_move,
        0
    )

    minus_dm = np.where(
        (down_move > up_move) & (down_move > 0),
        down_move,
        0
    )

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = tr.rolling(period).mean()

    plus_di = (
        100 *
        pd.Series(plus_dm, index=data.index)
        .rolling(period).mean() /
        atr
    )

    minus_di = (
        100 *
        pd.Series(minus_dm, index=data.index)
        .rolling(period).mean() /
        atr
    )

    dx = (
        100 *
        (plus_di - minus_di).abs() /
        (plus_di + minus_di).replace(0, np.nan)
    )

    adx = dx.rolling(period).mean()

    return adx


def calculate_indicators(data):

    data = data.copy()

    data["EMA20"] = data["Close"].ewm(
        span=20,
        adjust=False
    ).mean()

    data["EMA50"] = data["Close"].ewm(
        span=50,
        adjust=False
    ).mean()

    data["SMA200"] = data["Close"].rolling(200).mean()

    data["RSI"] = calculate_rsi(
        data["Close"]
    )

    (
        data["MACD"],
        data["MACD_SIGNAL"],
        data["MACD_HIST"]
    ) = calculate_macd(
        data["Close"]
    )

    data["ATR"] = calculate_atr(data)

    data["ADX"] = calculate_adx(data)

    data["BB_MIDDLE"] = (
        data["Close"].rolling(20).mean()
    )

    data["BB_STD"] = (
        data["Close"].rolling(20).std()
    )

    data["BB_UPPER"] = (
        data["BB_MIDDLE"] +
        2 * data["BB_STD"]
    )

    data["BB_LOWER"] = (
        data["BB_MIDDLE"] -
        2 * data["BB_STD"]
    )

    return data


# ============================================================
# TELECHARGEMENT
# ============================================================

def download_market_data(
    ticker,
    timeframe
):

    settings = TIMEFRAMES[timeframe]

    try:

        data = yf.download(
            ticker,
            period=settings["period"],
            interval=settings["interval"],
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            return pd.DataFrame()

        if isinstance(
            data.columns,
            pd.MultiIndex
        ):
            data.columns = (
                data.columns
                .get_level_values(0)
            )

        required = [
            "Open",
            "High",
            "Low",
            "Close"
        ]

        data = data.dropna(
            subset=required
        )

        # H4 construit à partir du H1
        if timeframe == "H4":

            data = data.resample(
                "4h"
            ).agg(
                {
                    "Open": "first",
                    "High": "max",
                    "Low": "min",
                    "Close": "last"
                }
            )

            data = data.dropna()

        return data

    except Exception:

        return pd.DataFrame()


# ============================================================
# STRUCTURE DU MARCHÉ
# ============================================================

def market_structure(data):

    if len(data) < 20:

        return {
            "structure": "Indéterminée",
            "bos": "Non confirmé",
            "support": np.nan,
            "resistance": np.nan
        }

    recent = data.tail(20)

    support = float(
        recent["Low"].min()
    )

    resistance = float(
        recent["High"].max()
    )

    current_price = float(
        data["Close"].iloc[-1]
    )

    previous_price = float(
        data["Close"].iloc[-5]
    )

    if (
        current_price > previous_price
        and current_price > data["EMA20"].iloc[-1]
    ):

        structure = "Haussière"

    elif (
        current_price < previous_price
        and current_price < data["EMA20"].iloc[-1]
    ):

        structure = "Baissière"

    else:

        structure = "Neutre"

    previous_resistance = float(
        data["High"].tail(10).max()
    )

    previous_support = float(
        data["Low"].tail(10).min()
    )

    if current_price > previous_resistance:

        bos = "BOS haussier potentiel"

    elif current_price < previous_support:

        bos = "BOS baissier potentiel"

    else:

        bos = "Pas de BOS clair"

    return {
        "structure": structure,
        "bos": bos,
        "support": support,
        "resistance": resistance
    }


# ============================================================
# FIBONACCI
# ============================================================

def calculate_fibonacci(data):

    recent = data.tail(100)

    swing_high = float(
        recent["High"].max()
    )

    swing_low = float(
        recent["Low"].min()
    )

    difference = swing_high - swing_low

    if difference <= 0:

        return {}

    levels = {

        "23.6%": swing_high - (
            difference * 0.236
        ),

        "38.2%": swing_high - (
            difference * 0.382
        ),

        "50.0%": swing_high - (
            difference * 0.500
        ),

        "61.8%": swing_high - (
            difference * 0.618
        ),

        "78.6%": swing_high - (
            difference * 0.786
        ),

        "127.2%": swing_high + (
            difference * 0.272
        ),

        "161.8%": swing_high + (
            difference * 0.618
        )
    }

    return levels


# ============================================================
# ANALYSE D'UN TIMEFRAME
# ============================================================

def analyze_timeframe(data):

    if data.empty or len(data) < 30:

        return None

    data = calculate_indicators(data)

    latest = data.iloc[-1]

    price = float(
        latest["Close"]
    )

    score = 0

    reasons = []

    # EMA20 / EMA50
    if latest["EMA20"] > latest["EMA50"]:

        score += 1

        reasons.append(
            "EMA20 > EMA50"
        )

    else:

        score -= 1

        reasons.append(
            "EMA20 < EMA50"
        )

    # SMA200
    if not pd.isna(
        latest["SMA200"]
    ):

        if price > latest["SMA200"]:

            score += 1

            reasons.append(
                "Prix > SMA200"
            )

        else:

            score -= 1

            reasons.append(
                "Prix < SMA200"
            )

    # RSI
    rsi = latest["RSI"]

    if not pd.isna(rsi):

        if rsi > 55:

            score += 1

            reasons.append(
                "RSI haussier"
            )

        elif rsi < 45:

            score -= 1

            reasons.append(
                "RSI baissier"
            )

        else:

            reasons.append(
                "RSI neutre"
            )

    # MACD
    if not pd.isna(
        latest["MACD"]
    ):

        if latest["MACD"] > latest["MACD_SIGNAL"]:

            score += 1

            reasons.append(
                "MACD haussier"
            )

        else:

            score -= 1

            reasons.append(
                "MACD baissier"
            )

    # ADX
    adx = latest["ADX"]

    if not pd.isna(adx):

        if adx >= 25:

            reasons.append(
                f"ADX fort ({adx:.1f})"
            )

        else:

            reasons.append(
                f"ADX faible ({adx:.1f})"
            )

    structure = market_structure(
        data
    )

    if structure["structure"] == "Haussière":

        score += 1

    elif structure["structure"] == "Baissière":

        score -= 1

    return {
        "data": data,
        "price": price,
        "score": score,
        "rsi": rsi,
        "adx": adx,
        "structure": structure,
        "reasons": reasons
    }


# ============================================================
# ANALYSE MULTI-TIMEFRAME
# ============================================================

if st.button(
    "🔍 ANALYSER LE MARCHÉ",
    use_container_width=True
):

    with st.spinner(
        "Analyse D1 → H4 → H1 → M15 → M5..."
    ):

        analyses = {}

        for tf in [
            "D1",
            "H4",
            "H1",
            "M15",
            "M5"
        ]:

            data = download_market_data(
                ticker,
                tf
            )

            result = analyze_timeframe(
                data
            )

            if result is not None:

                analyses[tf] = result

        # ====================================================
        # VÉRIFICATION
        # ====================================================

        if not analyses:

            st.error(
                "❌ Impossible de récupérer les données du marché."
            )

            st.stop()

        # ====================================================
        # SCORE GLOBAL
        # ====================================================

        weights = {
            "D1": 3,
            "H4": 3,
            "H1": 2,
            "M15": 1,
            "M5": 1
        }

        weighted_score = 0
        total_weight = 0

        for tf, result in analyses.items():

            weighted_score += (
                result["score"] *
                weights[tf]
            )

            total_weight += weights[tf]

        # ====================================================
        # DÉCISION
        # ====================================================

        if weighted_score >= 8:

            signal = "ACHAT"
            signal_class = "signal-buy"

        elif weighted_score <= -8:

            signal = "VENTE"
            signal_class = "signal-sell"

        elif abs(weighted_score) >= 3:

            signal = "ATTENDRE"
            signal_class = "signal-wait"

        else:

            signal = "AUCUN SETUP"
            signal_class = "signal-none"

        # ====================================================
        # AFFICHAGE GLOBAL
        # ====================================================

        st.divider()

        st.subheader(
            f"🎯 Décision globale : {asset}"
        )

        c1, c2, c3 = st.columns(3)

        current_price = list(
            analyses.values()
        )[-1]["price"]

        c1.metric(
            "Prix",
            f"{current_price:.5f}"
        )

        c2.metric(
            "Score pondéré",
            f"{weighted_score:+d}"
        )

        c3.metric(
            "Timeframes analysés",
            str(len(analyses))
        )

        st.markdown(
            f'<div class="{signal_class}">'
            f'{signal}'
            f'</div>',
            unsafe_allow_html=True
        )

        # ====================================================
        # TABLEAU TIMEFRAMES
        # ====================================================

        st.divider()

        st.subheader(
            "📊 Analyse multi-timeframe"
        )

        rows = []

        for tf in [
            "D1",
            "H4",
            "H1",
            "M15",
            "M5"
        ]:

            if tf not in analyses:
                continue

            result = analyses[tf]

            rows.append(
                {
                    "Timeframe": tf,
                    "Score": result["score"],
                    "RSI": (
                        round(
                            float(result["rsi"]),
                            2
                        )
                        if not pd.isna(
                            result["rsi"]
                        )
                        else "N/A"
                    ),
                    "ADX": (
                        round(
                            float(result["adx"]),
                            2
                        )
                        if not pd.isna(
                            result["adx"]
                        )
                        else "N/A"
                    ),
                    "Structure":
                        result[
                            "structure"
                        ]["structure"],
                    "BOS":
                        result[
                            "structure"
                        ]["bos"]
                }
            )

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

        # ====================================================
        # GRAPHIQUE
        # ====================================================

        st.divider()

        st.subheader(
            f"📈 Graphique {chart_tf}"
        )

        if chart_tf in analyses:

            chart_data = analyses[
                chart_tf
            ]["data"]

            chart = chart_data[
                [
                    "Close",
                    "EMA20",
                    "EMA50",
                    "SMA200"
                ]
            ].dropna()

            st.line_chart(
                chart
            )

        # ====================================================
        # STRUCTURE
        # ====================================================

        st.divider()

        st.subheader(
            "🧱 Structure du marché"
        )

        selected = analyses.get(
            chart_tf
        )

        if selected:

            structure = selected[
                "structure"
            ]

            s1, s2, s3 = st.columns(3)

            s1.metric(
                "Structure",
                structure["structure"]
            )

            s2.metric(
                "Support",
                (
                    f'{structure["support"]:.5f}'
                    if not pd.isna(
                        structure["support"]
                    )
                    else "N/A"
                )
            )

            s3.metric(
                "Résistance",
                (
                    f'{structure["resistance"]:.5f}'
                    if not pd.isna(
                        structure["resistance"]
                    )
                    else "N/A"
                )
            )

            st.info(
                f'BOS : {structure["bos"]}'
            )

        # ====================================================
        # FIBONACCI
        # ====================================================

        st.divider()

        st.subheader(
            "📐 Fibonacci"
        )

        if selected:

            fib = calculate_fibonacci(
                selected["data"]
            )

            if fib:

                fib_df = pd.DataFrame(
                    {
                        "Niveau": list(
                            fib.keys()
                        ),
                        "Prix": [
                            round(
                                value,
                                5
                            )
                            for value in fib.values()
                        ]
                    }
                )

                st.dataframe(
                    fib_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    "Les niveaux de Fibonacci servent "
                    "uniquement de zones de confluence."
                )

        # ====================================================
        # EXPLICATION
        # ====================================================

        st.divider()

        st.subheader(
            "🧠 P
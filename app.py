import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Forex AI Analyst",
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
    font-size: 2.4rem;
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
    font-size: 28px;
    font-weight: 800;
}

.signal-sell {
    padding: 18px;
    border-radius: 12px;
    background-color: #ffe0e0;
    border: 1px solid #d85c5c;
    text-align: center;
    font-size: 28px;
    font-weight: 800;
}

.signal-wait {
    padding: 18px;
    border-radius: 12px;
    background-color: #fff1cc;
    border: 1px solid #d6a83d;
    text-align: center;
    font-size: 28px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# TITRE
# ============================================================

st.markdown(
    '<div class="title">📈 Forex AI Analyst</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Analyse technique multi-indicateurs du marché Forex</div>',
    unsafe_allow_html=True
)

# ============================================================
# PARAMÈTRES
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    asset = st.selectbox(
        "Instrument",
        ["EUR/USD", "XAU/USD"]
    )

with col2:
    timeframe = st.selectbox(
        "Unité de temps",
        ["5m", "15m", "1h", "4h", "1d"]
    )

with col3:
    period = st.selectbox(
        "Historique",
        ["5d", "1mo", "3mo", "6mo", "1y"]
    )

ticker_map = {
    "EUR/USD": "EURUSD=X",
    "XAU/USD": "XAUUSD=X"
}

ticker = ticker_map[asset]

# ============================================================
# FONCTIONS TECHNIQUES
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
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()

    return macd, signal


def calculate_atr(data, period=14):
    high_low = data["High"] - data["Low"]

    high_close = (
        data["High"] - data["Close"].shift()
    ).abs()

    low_close = (
        data["Low"] - data["Close"].shift()
    ).abs()

    true_range = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    return true_range.rolling(period).mean()


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

    data["RSI"] = calculate_rsi(data["Close"])

    data["MACD"], data["MACD_SIGNAL"] = calculate_macd(
        data["Close"]
    )

    data["ATR"] = calculate_atr(data)

    data["BB_MIDDLE"] = data["Close"].rolling(20).mean()

    data["BB_STD"] = data["Close"].rolling(20).std()

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
# CHARGEMENT DU MARCHÉ
# ============================================================

if st.button("🔄 Analyser le marché", use_container_width=True):

    with st.spinner("Récupération et analyse des données..."):

        try:

            data = yf.download(
                ticker,
                period=period,
                interval=timeframe,
                progress=False,
                auto_adjust=False
            )

            if data.empty:
                st.error(
                    "❌ Aucune donnée disponible pour cet instrument."
                )
                st.stop()

            # Gestion des colonnes Yahoo Finance
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            required_columns = [
                "Open",
                "High",
                "Low",
                "Close"
            ]

            data = data.dropna(
                subset=required_columns
            )

            if len(data) < 30:
                st.warning(
                    "⚠️ Pas assez de données pour une analyse complète."
                )

            data = calculate_indicators(data)

            latest = data.iloc[-1]

            price = float(latest["Close"])

            # ====================================================
            # SCORE TECHNIQUE
            # ====================================================

            score = 0
            reasons = []

            # Tendance EMA
            if latest["EMA20"] > latest["EMA50"]:
                score += 1
                reasons.append(
                    "EMA20 au-dessus de EMA50 : tendance haussière."
                )
            else:
                score -= 1
                reasons.append(
                    "EMA20 sous EMA50 : tendance baissière."
                )

            # SMA200
            if not pd.isna(latest["SMA200"]):

                if price > latest["SMA200"]:
                    score += 1
                    reasons.append(
                        "Prix au-dessus de SMA200."
                    )
                else:
                    score -= 1
                    reasons.append(
                        "Prix sous SMA200."
                    )

            # RSI
            rsi = latest["RSI"]

            if not pd.isna(rsi):

                if rsi > 55:
                    score += 1
                    reasons.append(
                        "RSI supérieur à 55 : momentum haussier."
                    )

                elif rsi < 45:
                    score -= 1
                    reasons.append(
                        "RSI inférieur à 45 : momentum baissier."
                    )

                else:
                    reasons.append(
                        "RSI neutre."
                    )

            # MACD
            if (
                not pd.isna(latest["MACD"])
                and not pd.isna(latest["MACD_SIGNAL"])
            ):

                if latest["MACD"] > latest["MACD_SIGNAL"]:
                    score += 1
                    reasons.append(
                        "MACD au-dessus de son signal."
                    )
                else:
                    score -= 1
                    reasons.append(
                        "MACD sous son signal."
                    )

            # ====================================================
            # SIGNAL
            # ====================================================

            if score >= 3:
                signal = "ACHAT"
                signal_class = "signal-buy"

            elif score <= -3:
                signal = "VENTE"
                signal_class = "signal-sell"

            else:
                signal = "ATTENDRE"
                signal_class = "signal-wait"

            confidence = min(
                95,
                50 + abs(score) * 10
            )

            # ====================================================
            # RISQUE / NIVEAUX
            # ====================================================

            atr = latest["ATR"]

            if pd.isna(atr) or atr <= 0:
                atr = price * 0.005

            if signal == "ACHAT":

                entry = price
                stop_loss = price - (1.5 * atr)
                tp1 = price + (1.5 * atr)
                tp2 = price + (3 * atr)

            elif signal == "VENTE":

                entry = price
                stop_loss = price + (1.5 * atr)
                tp1 = price - (1.5 * atr)
                tp2 = price - (3 * atr)

            else:

                entry = price
                stop_loss = np.nan
                tp1 = np.nan
                tp2 = np.nan

            # ====================================================
            # AFFICHAGE
            # ====================================================

            st.divider()

            st.subheader(
                f"🎯 Analyse : {asset}"
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Prix",
                f"{price:.5f}"
            )

            c2.metric(
                "Score",
                f"{score:+d}"
            )

            c3.metric(
                "Confiance",
                f"{confidence}%"
            )

            c4.metric(
                "RSI",
                f"{rsi:.2f}" if not pd.isna(rsi) else "N/A"
            )

            st.markdown(
                f'<div class="{signal_class}">{signal}</div>',
                unsafe_allow_html=True
            )

            st.write("")

            # ====================================================
            # NIVEAUX
            # ====================================================

            if signal != "ATTENDRE":

                n1, n2, n3, n4 = st.columns(4)

                n1.metric(
                    "Entrée",
                    f"{entry:.5f}"
                )

                n2.metric(
                    "Stop Loss",
                    f"{stop_loss:.5f}"
                )

                n3.metric(
                    "TP1",
                    f"{tp1:.5f}"
                )

                n4.metric(
                    "TP2",
                    f"{tp2:.5f}"
                )

                st.info(
                    "⚠️ Les niveaux sont calculés automatiquement "
                    "à partir de la volatilité ATR. Ils ne constituent "
                    "pas une garantie de résultat."
                )

            # ====================================================
            # ONGLETS
            # ====================================================

            tab1, tab2, tab3 = st.tabs(
                [
                    "📊 Graphique",
                    "🧠 Explication",
                    "📋 Données"
                ]
            )

            with tab1:

                chart_data = data[
                    [
                        "Close",
                        "EMA20",
                        "EMA50",
                        "SMA200"
                    ]
                ].dropna()

                st.line_chart(
                    chart_data
                )

            with tab2:

                st.subheader(
                    "Pourquoi cette décision ?"
                )

                for reason in reasons:
                    st.write(
                        f"• {reason}"
                    )

                st.write("")

                if signal == "ACHAT":

                    st.success(
                        "Le contexte technique présente "
                        "davantage de facteurs haussiers."
                    )

                elif signal == "VENTE":

                    st.error(
                        "Le contexte technique présente "
                        "davantage de facteurs baissiers."
                    )

                else:

                    st.warning(
                        "Les indicateurs ne sont pas suffisamment "
                        "alignés. Il est préférable d'attendre."
                    )

            with tab3:

                st.dataframe(
                    data.tail(50),
                    use_container_width=True
                )

            # ====================================================
            # AVERTISSEMENT
            # ====================================================

            st.divider()

            st.caption(
                "Forex AI Analyst est un outil d'analyse technique. "
                "Aucune décision automatique de trading n'est exécutée. "
                "Les signaux ne constituent pas un conseil financier."
            )

        except Exception as error:

            st.error(
                "❌ Une erreur est survenue lors de l'analyse."
            )

            st.code(
                str(error)
            )

else:

    st.info(
        "👆 Choisis un instrument et une unité de temps, "
        "puis appuie sur « Analyser le marché »."
    )

    st.markdown("""
    ### 🔎 Ce que cette première version prépare

    **Analyse technique**
    - EMA 20
    - EMA 50
    - SMA 200
    - RSI
    - MACD
    - ATR
    - Bandes de Bollinger

    **Décision**
    - 🟢 ACHAT
    - 🔴 VENTE
    - 🟡 ATTENDRE

    **Gestion de position**
    - Entrée
    - Stop Loss
    - TP1
    - TP2
    - Score technique
    - Niveau de confiance

    **Marchés**
    - EUR/USD
    - XAU/USD
    """)
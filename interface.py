# ============================================================
# FOREX AI ANALYST
# Interface professionnelle du tableau de bord
# ============================================================

import pandas as pd
import streamlit as st

from config import (
    APP_SETTINGS,
    TIMEFRAME_ORDER,
    TIMEFRAMES,
)


# ============================================================
# EN-TÊTE
# ============================================================

def render_header(instrument_name: str, ticker: str):
    st.title("📊 Forex AI Analyst")

    st.caption(
        f"{APP_SETTINGS['SUBTITLE']} • "
        f"Instrument : {instrument_name} ({ticker})"
    )

    st.info(
        "⚠️ Analyse théorique uniquement : "
        "aucun ordre n'est envoyé automatiquement à un broker."
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar(instruments: dict):
    st.sidebar.header("⚙️ Configuration")

    instrument_names = list(instruments.keys())

    selected_instrument = st.sidebar.selectbox(
        "Instrument",
        instrument_names,
        index=0,
    )

    st.sidebar.divider()

    st.sidebar.subheader("🕐 Timeframes")

    selected_timeframes = []

    for timeframe in TIMEFRAME_ORDER:
        enabled = st.sidebar.checkbox(
            f"{timeframe} • {TIMEFRAMES[timeframe]['role']}",
            value=True,
            key=f"tf_{timeframe}",
        )

        if enabled:
            selected_timeframes.append(timeframe)

    st.sidebar.divider()

    st.sidebar.subheader("🛡️ Gestion du risque")

    st.sidebar.metric(
        "Risque / trade",
        "1 %",
    )

    st.sidebar.metric(
        "Risque total maximum",
        "2 %",
    )

    st.sidebar.metric(
        "R:R minimum",
        "1 : 2",
    )

    st.sidebar.divider()

    st.sidebar.caption(
        f"Version {APP_SETTINGS['VERSION']}"
    )

    st.sidebar.caption(
        "🟢 Trading automatique : DÉSACTIVÉ"
    )

    return selected_instrument, selected_timeframes


# ============================================================
# BADGE DE DIRECTION
# ============================================================

def _decision_color(decision: str) -> str:
    if decision == "ACHAT":
        return "🟢"

    if decision == "VENTE":
        return "🔴"

    if decision == "ATTENDRE":
        return "🟠"

    if decision == "AUCUN SETUP":
        return "⚪"

    return "⚪"


def render_global_decision(analysis: dict):
    decision = analysis.get("decision", "ATTENDRE")
    score = analysis.get("global_score", 0)
    confidence = analysis.get("confidence", 0)

    icon = _decision_color(decision)

    st.subheader("🎯 Décision globale")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Décision",
            f"{icon} {decision}",
        )

    with col2:
        st.metric(
            "Score global",
            f"{score:.2f}",
        )

    with col3:
        st.metric(
            "Confiance",
            f"{confidence:.0f} %",
        )


# ============================================================
# RÉSUMÉ GLOBAL
# ============================================================

def render_summary(analysis: dict):
    st.subheader("📌 Résumé de l'analyse")

    alignment = analysis.get("alignment", {})

    bullish = alignment.get("bullish", 0)
    bearish = alignment.get("bearish", 0)
    neutral = alignment.get("neutral", 0)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🟢 Timeframes haussiers",
            bullish,
        )

    with col2:
        st.metric(
            "🔴 Timeframes baissiers",
            bearish,
        )

    with col3:
        st.metric(
            "⚪ Timeframes neutres",
            neutral,
        )

    explanation = analysis.get(
        "summary",
        "Aucun résumé disponible.",
    )

    st.write(explanation)


# ============================================================
# TABLEAU MULTI-TIMEFRAME
# ============================================================

def render_timeframe_table(analysis: dict):
    st.subheader("🕐 Analyse multi-timeframe")

    timeframe_results = analysis.get(
        "timeframes",
        {},
    )

    rows = []

    for timeframe in TIMEFRAME_ORDER:

        result = timeframe_results.get(timeframe)

        if not result:
            continue

        decision = result.get(
            "direction",
            "NEUTRE",
        )

        score = result.get(
            "score",
            0,
        )

        confidence = result.get(
            "confidence",
            0,
        )

        weight = TIMEFRAMES[timeframe]["weight"]

        role = TIMEFRAMES[timeframe]["role"]

        rows.append(
            {
                "TF": timeframe,
                "Rôle": role,
                "Poids": weight,
                "Score": round(score, 2),
                "Direction": decision,
                "Confiance": f"{confidence:.0f} %",
            }
        )

    if not rows:
        st.warning(
            "Aucune donnée multi-timeframe disponible."
        )
        return

    dataframe = pd.DataFrame(rows)

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# DÉTAILS PAR TIMEFRAME
# ============================================================

def render_timeframe_details(analysis: dict):
    st.subheader("🔎 Détails par timeframe")

    timeframe_results = analysis.get(
        "timeframes",
        {},
    )

    for timeframe in TIMEFRAME_ORDER:

        result = timeframe_results.get(timeframe)

        if not result:
            continue

        direction = result.get(
            "direction",
            "NEUTRE",
        )

        score = result.get(
            "score",
            0,
        )

        confidence = result.get(
            "confidence",
            0,
        )

        with st.expander(
            f"{timeframe} • {direction} • "
            f"Score {score:.2f}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Direction",
                    direction,
                )

            with col2:
                st.metric(
                    "Score",
                    f"{score:.2f}",
                )

            with col3:
                st.metric(
                    "Confiance",
                    f"{confidence:.0f} %",
                )

            indicators = result.get(
                "indicators",
                {},
            )

            if indicators:

                st.markdown("**Indicateurs principaux**")

                indicator_rows = []

                for name, value in indicators.items():

                    if isinstance(value, float):
                        value = round(value, 4)

                    indicator_rows.append(
                        {
                            "Indicateur": name,
                            "Valeur": value,
                        }
                    )

                st.dataframe(
                    pd.DataFrame(indicator_rows),
                    use_container_width=True,
                    hide_index=True,
                )

            structure = result.get(
                "structure",
                {},
            )

            if structure:

                st.markdown("**Structure du marché**")

                structure_direction = structure.get(
                    "trend",
                    "NEUTRE",
                )

                bos = structure.get(
                    "bos",
                    "NONE",
                )

                st.write(
                    f"Structure : **{structure_direction}**"
                )

                st.write(
                    f"BOS : **{bos}**"
                )


# ============================================================
# GRAPHIQUE
# ============================================================

def render_chart(data: pd.DataFrame, title: str):
    st.subheader(f"📈 Graphique • {title}")

    if data is None or data.empty:
        st.warning(
            "Aucune donnée disponible pour le graphique."
        )
        return

    chart_data = data.copy()

    if "Close" not in chart_data.columns:
        st.warning(
            "Les données ne contiennent pas de cours de clôture."
        )
        return

    columns = ["Close"]

    for column in [
        "EMA20",
        "EMA50",
        "SMA200",
        "BB_Upper",
        "BB_Middle",
        "BB_Lower",
    ]:
        if column in chart_data.columns:
            columns.append(column)

    chart_data = chart_data[columns].tail(300)

    st.line_chart(
        chart_data,
        use_container_width=True,
    )


# ============================================================
# NIVEAUX DE TRADING
# ============================================================

def render_trade_levels(risk_analysis: dict):
    st.subheader("🎯 Niveaux théoriques")

    if not risk_analysis:
        st.info(
            "Aucun niveau de trading disponible."
        )
        return

    decision = risk_analysis.get(
        "decision",
        "ATTENDRE",
    )

    if decision not in ["ACHAT", "VENTE"]:
        st.warning(
            "Aucun niveau d'entrée n'est proposé "
            "car les conditions ne sont pas suffisamment "
            "alignées."
        )
        return

    entry = risk_analysis.get("entry")
    stop_loss = risk_analysis.get("stop_loss")
    tp1 = risk_analysis.get("tp1")
    tp2 = risk_analysis.get("tp2")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Entrée",
            _format_price(entry),
        )

    with col2:
        st.metric(
            "Stop Loss",
            _format_price(stop_loss),
        )

    with col3:
        st.metric(
            "TP1",
            _format_price(tp1),
        )

    with col4:
        st.metric(
            "TP2",
            _format_price(tp2),
        )

    rr1 = risk_analysis.get(
        "rr_tp1",
        0,
    )

    rr2 = risk_analysis.get(
        "rr_tp2",
        0,
    )

    st.write(
        f"**R:R TP1 :** 1:{rr1:.2f}  |  "
        f"**R:R TP2 :** 1:{rr2:.2f}"
    )


# ============================================================
# FIBONACCI
# ============================================================

def render_fibonacci(fibonacci_analysis: dict):
    st.subheader("📐 Fibonacci")

    if not fibonacci_analysis:
        st.info(
            "Aucune analyse Fibonacci disponible."
        )
        return

    levels = fibonacci_analysis.get(
        "levels",
        {},
    )

    if not levels:
        st.info(
            "Aucun niveau Fibonacci exploitable."
        )
        return

    rows = []

    for level, price in levels.items():

        rows.append(
            {
                "Niveau": level,
                "Prix": round(float(price), 6),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )

    nearest = fibonacci_analysis.get(
        "nearest",
    )

    if nearest:
        st.write(
            f"📍 Niveau Fibonacci le plus proche : "
            f"**{nearest}**"
        )

    confluence = fibonacci_analysis.get(
        "confluence",
    )

    if confluence:
        st.write(
            f"🔗 Confluence : **{confluence}**"
        )


# ============================================================
# INFORMATIONS DU MARCHÉ
# ============================================================

def render_market_info(
    price,
    data: pd.DataFrame,
):
    st.subheader("💰 Marché")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Prix actuel",
            _format_price(price),
        )

    with col2:
        rows = len(data) if data is not None else 0

        st.metric(
            "Bougies disponibles",
            rows,
        )

    with col3:
        if data is not None and not data.empty:
            last_date = data.index[-1]
            st.metric(
                "Dernière donnée",
                str(last_date)[:16],
            )
        else:
            st.metric(
                "Dernière donnée",
                "N/A",
            )


# ============================================================
# RISQUE
# ============================================================

def render_risk(risk_analysis: dict):
    st.subheader("🛡️ Gestion du risque")

    if not risk_analysis:
        st.info(
            "Aucune analyse de risque disponible."
        )
        return

    valid_rr = risk_analysis.get(
        "valid_rr",
        False,
    )

    risk_per_trade = risk_analysis.get(
        "risk_per_trade",
        0.01,
    )

    max_total_risk = risk_analysis.get(
        "max_total_risk",
        0.02,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Risque / trade",
            f"{risk_per_trade * 100:.1f} %",
        )

    with col2:
        st.metric(
            "Risque maximum total",
            f"{max_total_risk * 100:.1f} %",
        )

    with col3:

        if valid_rr:
            st.metric(
                "R:R minimum",
                "✅ Respecté",
            )
        else:
            st.metric(
                "R:R minimum",
                "❌ Non respecté",
            )

    st.caption(
        "Les calculs de risque sont théoriques. "
        "L'application ne passe aucun ordre."
    )


# ============================================================
# DONNÉES RÉCENTES
# ============================================================

def render_latest_data(data: pd.DataFrame):
    st.subheader("🧾 Données récentes")

    if data is None or data.empty:
        st.warning(
            "Aucune donnée récente disponible."
        )
        return

    display_columns = [
        column
        for column in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "EMA20",
            "EMA50",
            "SMA200",
            "RSI",
            "MACD",
            "MACD_Signal",
            "ATR",
            "ADX",
            "BB_Upper",
            "BB_Middle",
            "BB_Lower",
            "Stoch_K",
            "Stoch_D",
        ]
        if column in data.columns
    ]

    latest = data[display_columns].tail(10).copy()

    st.dataframe(
        latest,
        use_container_width=True,
    )


# ============================================================
# AVERTISSEMENTS
# ============================================================

def render_warnings(
    analysis: dict,
    risk_analysis: dict,
):
    st.subheader("⚠️ Contrôles")

    warnings = []

    decision = analysis.get(
        "decision",
        "ATTENDRE",
    )

    if decision == "ATTENDRE":
        warnings.append(
            "Le marché ne présente pas suffisamment "
            "de confluence pour une décision forte."
        )

    if decision == "AUCUN SETUP":
        warnings.append(
            "Aucun setup valide n'a été détecté."
        )

    if risk_analysis:
        valid_rr = risk_analysis.get(
            "valid_rr",
            False,
        )

        if not valid_rr:
            warnings.append(
                "Le ratio risque/rendement minimum "
                "n'est pas respecté."
            )

    if not warnings:
        st.success(
            "✅ Aucun avertissement critique détecté."
        )
        return

    for warning in warnings:
        st.warning(warning)


# ============================================================
# PIED DE PAGE
# ============================================================

def render_footer():
    st.divider()

    st.caption(
        "Forex AI Analyst • Analyse technique multi-timeframe"
    )

    st.caption(
        "⚠️ Outil d'analyse et d'aide à la décision. "
        "Ce système ne garantit aucun résultat financier."
    )


# ============================================================
# UTILITAIRE PRIX
# ============================================================

def _format_price(price):
    if price is None:
        return "N/A"

    try:
        value = float(price)

        if value >= 100:
            return f"{value:.2f}"

        return f"{value:.5f}"

    except (TypeError, ValueError):
        return "N/A"
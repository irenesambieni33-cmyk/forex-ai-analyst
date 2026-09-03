# ============================================================
# FOREX AI ANALYST
# Application principale
# ============================================================

import streamlit as st

from config import (
    APP_SETTINGS,
    INSTRUMENTS,
    TIMEFRAME_ORDER,
)

from data import (
    load_timeframe_data,
    get_last_price,
)

from indicators import (
    add_all_indicators,
)

from analysis import (
    analyze_all_timeframes,
)

from fibonacci import (
    analyze_fibonacci,
)

from risk import (
    analyze_risk,
)

from interface import (
    render_header,
    render_sidebar,
    render_global_decision,
    render_summary,
    render_timeframe_table,
    render_timeframe_details,
    render_chart,
    render_trade_levels,
    render_fibonacci,
    render_market_info,
    render_risk,
    render_latest_data,
    render_warnings,
    render_footer,
)


# ============================================================
# CONFIGURATION STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Forex AI Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        padding: 12px;
        border-radius: 10px;
    }

    .block-container {
        max-width: 1500px;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TITRE
# ============================================================

st.title("📊 Forex AI Analyst")

st.caption(
    "Analyse technique multi-timeframe • "
    "D1 → H4 → H1 → M15 → M5 • "
    "Aucun ordre automatique"
)


# ============================================================
# SIDEBAR
# ============================================================

selected_instrument, selected_timeframes = render_sidebar(
    INSTRUMENTS
)


# ============================================================
# VÉRIFICATION DES TIMEFRAMES
# ============================================================

if not selected_timeframes:

    st.warning(
        "⚠️ Sélectionne au moins un timeframe "
        "dans la barre latérale."
    )

    render_footer()

    st.stop()


# ============================================================
# INFORMATIONS INSTRUMENT
# ============================================================

instrument_config = INSTRUMENTS[
    selected_instrument
]

ticker = instrument_config["ticker"]
instrument_name = instrument_config["name"]

render_header(
    instrument_name=selected_instrument,
    ticker=ticker,
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

with st.spinner(
    f"📡 Récupération des données de {selected_instrument}..."
):

    timeframe_data = {}

    loading_errors = []

    for timeframe in TIMEFRAME_ORDER:

        if timeframe not in selected_timeframes:
            continue

        data = load_timeframe_data(
            ticker=ticker,
            timeframe=timeframe,
        )

        if data is None or data.empty:

            loading_errors.append(
                timeframe
            )

            continue

        try:

            data = add_all_indicators(
                data
            )

        except Exception as error:

            loading_errors.append(
                f"{timeframe} ({error})"
            )

            continue

        timeframe_data[timeframe] = data


# ============================================================
# CONTRÔLE DES DONNÉES
# ============================================================

if loading_errors:

    st.warning(
        "⚠️ Certaines données n'ont pas pu être chargées : "
        + ", ".join(
            str(item)
            for item in loading_errors
        )
    )


if not timeframe_data:

    st.error(
        "❌ Aucune donnée exploitable n'a été récupérée."
    )

    st.info(
        "Vérifie la connexion Internet ou réessaie "
        "dans quelques instants."
    )

    render_footer()

    st.stop()


# ============================================================
# ANALYSE MULTI-TIMEFRAME
# ============================================================

with st.spinner(
    "🧠 Analyse technique en cours..."
):

    try:

        analysis = analyze_all_timeframes(
            timeframe_data
        )

    except Exception as error:

        st.error(
            "❌ Une erreur est survenue pendant "
            "l'analyse multi-timeframe."
        )

        st.exception(error)

        render_footer()

        st.stop()


# ============================================================
# PRIX ACTUEL
# ============================================================

reference_timeframe = "M5"

if reference_timeframe not in timeframe_data:

    reference_timeframe = list(
        timeframe_data.keys()
    )[0]

reference_data = timeframe_data[
    reference_timeframe
]

current_price = get_last_price(
    reference_data
)


# ============================================================
# FIBONACCI
# ============================================================

fibonacci_analysis = {}

try:

    fibonacci_analysis = analyze_fibonacci(
        reference_data
    )

except Exception:

    fibonacci_analysis = {}


# ============================================================
# GESTION DU RISQUE
# ============================================================

risk_analysis = {}

try:

    risk_analysis = analyze_risk(
        analysis=analysis,
        data=reference_data,
    )

except TypeError:

    try:

        risk_analysis = analyze_risk(
            analysis,
            reference_data,
        )

    except Exception:

        risk_analysis = {}

except Exception:

    risk_analysis = {}


# ============================================================
# TABLEAU PRINCIPAL
# ============================================================

render_global_decision(
    analysis
)

st.divider()

render_summary(
    analysis
)

st.divider()

render_timeframe_table(
    analysis
)


# ============================================================
# MARCHÉ
# ============================================================

st.divider()

render_market_info(
    current_price,
    reference_data,
)


# ============================================================
# GRAPHIQUE
# ============================================================

st.divider()

render_chart(
    reference_data,
    f"{selected_instrument} • {reference_timeframe}",
)


# ============================================================
# NIVEAUX DE TRADING
# ============================================================

st.divider()

render_trade_levels(
    risk_analysis
)


# ============================================================
# FIBONACCI
# ============================================================

st.divider()

render_fibonacci(
    fibonacci_analysis
)


# ============================================================
# RISQUE
# ============================================================

st.divider()

render_risk(
    risk_analysis
)


# ============================================================
# DÉTAILS DES TIMEFRAMES
# ============================================================

st.divider()

render_timeframe_details(
    analysis
)


# ============================================================
# DONNÉES RÉCENTES
# ============================================================

st.divider()

render_latest_data(
    reference_data
)


# ============================================================
# AVERTISSEMENTS
# ============================================================

st.divider()

render_warnings(
    analysis,
    risk_analysis,
)


# ============================================================
# PIED DE PAGE
# ============================================================

render_footer()
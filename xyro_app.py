"""
Xyro - Final Complete Streamlit App
Luxurious Purple + Black Theme
"""

import amlit as st
from ai_brain import AIBrain, SignalDirection
import datetime

st.set_page_config(page_title="Xyro", page_icon="🟣", layout="centered")

# Premium Dark Purple Theme
st.markdown("""
<style>
    .stApp { background-color: #0F0F12; color: #E0E0E0; }
    .main-title { font-size: 3.2rem; font-weight: 800; color: #A78BFA; text-align: center; }
    .greeting { font-size: 1.9rem; font-weight: 600; color: #C4B5FD; text-align: center; margin-bottom: 1.8rem; }
    .section-header { font-size: 1.25rem; font-weight: 700; color: #A78BFA; margin-top: 1.2rem; }
    .signal-card { 
        background-color: #1A1A20; 
        border: 1px solid #6B46C1; 
        border-radius: 18px; 
        padding: 26px; 
        margin: 18px 0;
        box-shadow: 0 4px 18px rgba(107, 70, 193, 0.2);
    }
    .stButton>button {
        background-color: #6B46C1; color: white; font-weight: 700;
        border-radius: 12px; padding: 14px 36px; font-size: 1.12rem; border: none;
    }
    .stButton>button:hover { background-color: #7C3AED; }
</style>
""", unsafe_allow_html=True)

if "latest_signal_index" not in st.session_state:
    st.session_state.latest_signal_index = None

# Header
st.markdown('<div class="main-title">Xyro</div>', unsafe_allow_html=True)
st.markdown('<div class="greeting">Hi Faiz!!!</div>', unsafe_allow_html=True)
st.caption("Personal AI Gold Signal Platform • Free Forever • Risk Management Locked")

# Market Status
st.markdown('<div class="section-header">Market Status</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.metric("XAUUSD", "—", "Live Data")
with col2:
    st.metric("Session", "London + NY", "High Activity")

st.divider()

# Analyze Button
if st.button("🔮 Analyze XAUUSD Now", use_container_width=True):
    with st.spinner("AI Brain is performing deep multi-technique analysis..."):
        try:
            brain = AIBrain()
            brain.set_news_impact("NEUTRAL")
            signal = brain.analyze("XAUUSD", account_balance=100.0)
        except Exception:
            st.error("Something went wrong while analyzing. Please try again.")
            st.stop()

    st.divider()

    if signal.direction == SignalDirection.NO_SIGNAL:
        st.error("**No High-Quality Signal Right Now**")
        st.write(signal.reason)
    else:
        st.markdown('<div class="signal-card">', unsafe_allow_html=True)

        direction_color = "#22C55E" if signal.direction.value == "BUY" else "#EF4444"
        st.markdown(f"<h2 style='color:{direction_color}; text-align:center;'>{signal.direction.value}</h2>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Entry", f"${signal.entry}")
        with col2: st.metric("Stop Loss", f"${signal.stop_loss}")
        with col3: st.metric("Position Size", f"{signal.position_size} lot")

        col1, col2 = st.columns(2)
        with col1: st.metric("Take Profit 1", f"${signal.take_profit_1}")
        with col2: st.metric("Take Profit 2", f"${signal.take_profit_2}")

        st.progress(signal.confidence / 100, text=f"Confidence: {signal.confidence}%")
        st.markdown("**AI Analysis Summary:**")
        st.write(signal.reason)

        st.markdown('</div>', unsafe_allow_html=True)
        st.success("High-quality signal generated. Follow your locked risk rules.")

        st.session_state.latest_signal_index = len(brain.historical_signals) - 1

        # Semi-Automatic Outcome
        st.divider()
        st.markdown("**📍 Check Current Price & Suggest Outcome**")

        if st.button("Check Latest Price & Suggest", use_container_width=True):
            suggestion = brain.suggest_outcome(st.session_state.latest_signal_index)

            if suggestion == "WIN":
                st.success("✅ Based on current price, this signal likely **HIT TP** (WIN)")
                if st.button("Confirm as WIN", use_container_width=True):
                    brain.record_outcome(st.session_state.latest_signal_index, "WIN")
                    st.success("Recorded as WIN. Thank you — AI is learning!")
            elif suggestion == "LOSS":
                st.error("❌ Based on current price, this signal likely **HIT SL** (LOSS)")
                if st.button("Confirm as LOSS", use_container_width=True):
                    brain.record_outcome(st.session_state.latest_signal_index, "LOSS")
                    st.error("Recorded as LOSS. AI will learn from this.")
            else:
                st.info("⏳ Current price shows the trade is **still open** or not decisive yet.")

        st.markdown("**Or record manually:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Hit TP", use_container_width=True):
                if st.session_state.latest_signal_index is not None:
                    brain.record_outcome(st.session_state.latest_signal_index, "WIN")
                    st.success("Recorded as WIN.")
        with col2:
            if st.button("❌ Hit SL", use_container_width=True):
                if st.session_state.latest_signal_index is not None:
                    brain.record_outcome(st.session_state.latest_signal_index, "LOSS")
                    st.error("Recorded as LOSS.")
        with col3:
            if st.button("⏳ Still Open", use_container_width=True):
                st.info("You can record later.")

st.caption(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")

# Performance Dashboard
st.divider()
st.markdown('<div class="section-header">Performance Dashboard</div>', unsafe_allow_html=True)

brain = AIBrain()
stats = brain.get_performance_summary()

if stats["total"] > 0:
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Signals", stats["total"])
    with col2: st.metric("Win Rate", f"{stats['win_rate']}%")
    with col3: st.metric("Wins / Losses", f"{stats['wins']} / {stats['losses']}")
    with col4: st.metric("Est. Total Pips", f"{stats['total_estimated_pips']}")

    st.markdown("**Direction Performance**")
    col1, col2 = st.columns(2)
    with col1: st.metric("BUY Win Rate", f"{stats['buy_win_rate']}%")
    with col2: st.metric("SELL Win Rate", f"{stats['sell_win_rate']}%")

    st.markdown("**AI Learning Insight**")
    st.info(f"Average confidence of winning signals: **{stats['avg_confidence_win']}%**")
else:
    st.info("No completed signals yet. Record outcomes to see your performance.")

# Recent Signals
st.divider()
st.markdown('<div class="section-header">Recent Signals</div>', unsafe_allow_html=True)

if brain.historical_signals:
    for sig in reversed(brain.historical_signals[-6:]):
        emoji = "🟢" if sig.direction.value == "BUY" else "🔴"
        outcome_text = f" → **{sig.outcome}** ({sig.estimated_pips} pips)" if sig.outcome else ""
        st.write(f"{emoji} **{sig.direction.value}** @ ${sig.entry} | Conf: {sig.confidence}%{outcome_text}")
else:
    st.info("No signals recorded yet.")

# How AI Learning Works
st.divider()
st.markdown('<div class="section-header">How AI Learning Works</div>', unsafe_allow_html=True)
st.info(
    "Xyro uses **Market Structure + Trend + Momentum** for analysis. "
    "Every outcome you record helps improve future signal quality."
)

# News Section
st.divider()
st.markdown('<div class="section-header">News & Macro</div>', unsafe_allow_html=True)
st.info("News impact module ready. Current bias: Neutral (adjustable in AI Brain)")

st.divider()

# How to Run
st.markdown('<div class="section-header">How to Run Xyro</div>', unsafe_allow_html=True)
st.code("""
# 1. Install packages (run once)
pip install streamlit yfinance pandas numpy

# 2. Run the app
streamlit run xyro_app.py
""", language="bash")

st.caption("Xyro • AI does the analysis. You just press one button. • Risk Management is permanently locked. Thank you for using Xyro!")

import streamlit as st
from ai_brain import AIBrain, SignalDirection
import datetime

st.set_page_config(page_title="Xyro", page_icon="🟣", layout="centered")

st.title("Xyro")
st.subheader("Hi Faiz!!!")
st.caption("Personal AI Gold Signal Platform • Free Forever")

if st.button("🔮 Analyze XAUUSD Now", use_container_width=True):
    with st.spinner("Analyzing..."):
        brain = AIBrain()
        brain.set_news_impact("NEUTRAL")
        signal = brain.analyze("XAUUSD", account_balance=100.0)

    if signal.direction == SignalDirection.NO_SIGNAL:
        st.error(signal.reason)
    else:
        st.success(f"**{signal.direction.value}** Signal")
        st.write(f"Entry: ${signal.entry}")
        st.write(f"Stop Loss: ${signal.stop_loss}")
        st.write(f"Take Profit 1: ${signal.take_profit_1}")
        st.write(f"Take Profit 2: ${signal.take_profit_2}")
        st.write(f"Confidence: {signal.confidence}%")
        st.write(signal.reason)

st.caption("Xyro • Risk Management Locked")

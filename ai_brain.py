from dataclasses import dataclass
from typing impornal, Dict, Any, List
from enum import Enum
import datetime
import pandas as pd
import numpy as np
import yfinance as yf

RISK_PER_TRADE = 0.005
MAX_DAILY_RISK = 0.01
MAX_OPEN_TRADES = 1
MIN_RISK_REWARD = 2.5
MIN_CONFIDENCE = 75
BASE_LOT_SIZE = 0.01

class SignalDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"
    NO_SIGNAL = "NO_SIGNAL"

@dataclass
class Signal:
    direction: SignalDirection
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    confidence: int = 0
    reason: str = ""
    position_size: float = 0.01
    timestamp: datetime.datetime = datetime.datetime.now()
    outcome: str = ""
    estimated_pips: float = 0.0

class AIBrain:
    def __init__(self):
        self.risk_per_trade = RISK_PER_TRADE
        self.max_daily_risk = MAX_DAILY_RISK
        self.max_open_trades = MAX_OPEN_TRADES
        self.min_confidence = MIN_CONFIDENCE
        self.base_lot_size = BASE_LOT_SIZE
        self.historical_signals: List[Signal] = []
        self.news_impact = "NEUTRAL"

    def set_news_impact(self, impact: str):
        self.news_impact = impact.upper()

    def fetch_data(self, symbol: str = "XAUUSD=X"):
        try:
            df = yf.download(symbol, period="60d", interval="1h", progress=False)
            if df.empty:
                return None
            return df.dropna()
        except:
            return None

    def calculate_indicators(self, df):
        indicators = {}
        try:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs)).iloc[-1]

            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            indicators['macd'] = (exp1 - exp2).iloc[-1]

            high_low = df['High'] - df['Low']
            true_range = high_low.rolling(14).mean().iloc[-1]
            indicators['atr'] = true_range

            indicators['sma_50'] = df['Close'].rolling(window=50).mean().iloc[-1]
            indicators['sma_200'] = df['Close'].rolling(window=200).mean().iloc[-1]
        except:
            indicators = {'rsi': 50, 'macd': 0, 'atr': 1.0, 'sma_50': 0, 'sma_200': 0}
        return indicators

    def calculate_confluence_score(self, indicators):
        score = 50
        try:
            if indicators['rsi'] < 35:
                score += 12
            elif indicators['rsi'] > 65:
                score -= 12

            if indicators['macd'] > 0:
                score += 8
            else:
                score -= 8

            if indicators['sma_50'] > indicators['sma_200']:
                score += 10
            else:
                score -= 10

            if self.news_impact == "BULLISH":
                score += 10
            elif self.news_impact == "BEARISH":
                score -= 10

            score = max(0, min(100, score))
        except:
            pass
        return int(score)

    def analyze(self, symbol="XAUUSD=X", account_balance=100.0):
        df = self.fetch_data(symbol)
        if df is None or len(df) < 50:
            return Signal(direction=SignalDirection.NO_SIGNAL, reason="Insufficient market data.")

        indicators = self.calculate_indicators(df)
        confluence = self.calculate_confluence_score(indicators)

        if confluence < self.min_confidence:
            return Signal(direction=SignalDirection.NO_SIGNAL, reason=f"Low confluence ({confluence}%).")

        current_price = float(df['Close'].iloc[-1])
        atr = indicators.get('atr', 1.0)

        direction = SignalDirection.BUY if indicators['sma_50'] > indicators['sma_200'] else SignalDirection.SELL

        if direction == SignalDirection.BUY:
            entry = round(current_price, 2)
            stop_loss = round(entry - (atr * 1.5), 2)
            take_profit_1 = round(entry + (atr * 2.5), 2)
            take_profit_2 = round(entry + (atr * 4.0), 2)
        else:
            entry = round(current_price, 2)
            stop_loss = round(entry + (atr * 1.5), 2)
            take_profit_1 = round(entry - (atr * 2.5), 2)
            take_profit_2 = round(entry - (atr * 4.0), 2)

        reason = f"Confluence {confluence}%. Trend favors {direction.value}."

        signal = Signal(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            confidence=confluence,
            reason=reason,
            position_size=round(self.base_lot_size, 2),
            timestamp=datetime.datetime.now()
        )

        self.historical_signals.append(signal)
        return signal

    def record_outcome(self, signal_index: int, outcome: str):
        if 0 <= signal_index < len(self.historical_signals):
            self.historical_signals[signal_index].outcome = outcome.upper()

    def suggest_outcome(self, signal_index: int) -> str:
        if not (0 <= signal_index < len(self.historical_signals)):
            return "STILL_OPEN"
        signal = self.historical_signals[signal_index]
        try:
            df = self.fetch_data("XAUUSD=X")
            current_price = float(df['Close'].iloc[-1])
            if signal.direction == SignalDirection.BUY:
                if current_price >= signal.take_profit_2:
                    return "WIN"
                elif current_price >= signal.take_profit_1:
                    return "WIN"
                elif current_price <= signal.stop_loss:
                    return "LOSS"
            else:
                if current_price <= signal.take_profit_2:
                    return "WIN"
                elif current_price <= signal.take_profit_1:
                    return "WIN"
                elif current_price >= signal.stop_loss:
                    return "LOSS"
            return "STILL_OPEN"
        except:
            return "STILL_OPEN"

    def get_performance_summary(self):
        if not self.historical_signals:
            return {"total": 0, "win_rate": 0, "wins": 0, "losses": 0}
        wins = sum(1 for s in self.historical_signals if s.outcome == "WIN")
        losses = sum(1 for s in self.historical_signals if s.outcome == "LOSS")
        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0
        return {"total": total, "win_rate": round(win_rate, 1), "wins": wins, "losses": losses}

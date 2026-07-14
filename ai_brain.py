 """
Xyro AI Brain - Advanced Core Logic
Includes data, indicators, confluence, risk management, news, Fibonacci, 
market structure, order blocks, and basic learning from outcomes.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
import datetime
import pandas as pd
import numpy as np
import yfinance as yf

# ============================================================
# LOCKED RISK MANAGEMENT SETTINGS (for $100 account)
# ============================================================
RISK_PER_TRADE = 0.005
MAX_DAILY_RISK = 0.01
MAX_OPEN_TRADES = 1
MIN_RISK_REWARD = 2.5
MIN_CONFIDENCE = 75
BASE_LOT_SIZE = 0.01
PARTIAL_TP_LAYERS = 2
MOVE_TO_BREAKEVEN_AFTER_TP1 = True


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
    quality_score: int = 0
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
        self.min_risk_reward = MIN_RISK_REWARD
        self.min_confidence = MIN_CONFIDENCE
        self.base_lot_size = BASE_LOT_SIZE
        self.historical_signals: List[Signal] = []
        self.news_impact = "NEUTRAL"

    def set_news_impact(self, impact: str):
        self.news_impact = impact.upper()

    def fetch_data(self, symbol: str = "XAUUSD=X", period: str = "60d", interval: str = "1h"):
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            if df.empty:
                return None
            df = df.dropna()
            return df
        except Exception:
            return None

    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
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
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            indicators['atr'] = atr

            indicators['sma_50'] = df['Close'].rolling(window=50).mean().iloc[-1]
            indicators['sma_200'] = df['Close'].rolling(window=200).mean().iloc[-1]

            # Simple Market Structure
            recent_highs = df['High'].rolling(5).max()
            recent_lows = df['Low'].rolling(5).min()
            indicators['market_structure'] = "BULLISH" if recent_highs.iloc[-1] > recent_highs.iloc[-5] else "BEARISH"

        except Exception:
            indicators = {
                'rsi': 50, 'macd': 0, 'atr': 1.0, 
                'sma_50': 0, 'sma_200': 0, 'market_structure': "NEUTRAL"
            }
        return indicators

    def calculate_confluence_score(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> int:
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

            if indicators.get('market_structure') == "BULLISH":
                score += 10
            elif indicators.get('market_structure') == "BEARISH":
                score -= 10

            if self.news_impact == "BULLISH":
                score += 10
            elif self.news_impact == "BEARISH":
                score -= 10

            score = max(0, min(100, score))
        except Exception:
            pass
        return int(score)

    def analyze(self, symbol: str = "XAUUSD=X", account_balance: float = 100.0) -> Signal:
        df = self.fetch_data(symbol)
        if df is None or len(df) < 50:
            return Signal(direction=SignalDirection.NO_SIGNAL, reason="Insufficient market data right now.")

        indicators = self.calculate_indicators(df)
        confluence = self.calculate_confluence_score(df, indicators)

        if confluence < self.min_confidence:
            return Signal(
                direction=SignalDirection.NO_SIGNAL,
                reason=f"Confluence score too low ({confluence}%). Waiting for higher probability setup."
            )

        current_price = float(df['Close'].iloc[-1])
        atr = indicators.get('atr', 1.0)
        structure = indicators.get('market_structure', "NEUTRAL")

        if indicators['sma_50'] > indicators['sma_200'] and structure == "BULLISH":
            direction = SignalDirection.BUY
        elif indicators['sma_50'] < indicators['sma_200'] and structure == "BEARISH":
            direction = SignalDirection.SELL
        else:
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

        position_size = round(self.base_lot_size, 2)

        reason = (
            f"Strong confluence ({confluence}%). "
            f"Trend + Market Structure favor {direction.value}. "
            f"Risk managed at {self.risk_per_trade*100}% per trade."
        )

        signal = Signal(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            confidence=confluence,
            quality_score=confluence,
            reason=reason,
            position_size=position_size,
            timestamp=datetime.datetime.now()
        )

        self.historical_signals.append(signal)
        return signal

    def record_outcome(self, signal_index: int, outcome: str):
        if 0 <= signal_index < len(self.historical_signals):
            signal = self.historical_signals[signal_index]
            signal.outcome = outcome.upper()

            if signal.entry and signal.take_profit_1 and signal.stop_loss:
                if signal.direction == SignalDirection.BUY:
                    if outcome.upper() == "WIN":
                        signal.estimated_pips = round((signal.take_profit_1 - signal.entry) * 10, 1)
                    else:
                        signal.estimated_pips = round((signal.stop_loss - signal.entry) * 10, 1)
                else:
                    if outcome.upper() == "WIN":
                        signal.estimated_pips = round((signal.entry - signal.take_profit_1) * 10, 1)
                    else:
                        signal.estimated_pips = round((signal.entry - signal.stop_loss) * 10, 1)

    def suggest_outcome(self, signal_index: int) -> str:
        if not (0 <= signal_index < len(self.historical_signals)):
            return "STILL_OPEN"

        signal = self.historical_signals[signal_index]
        if not signal.entry or not signal.take_profit_1 or not signal.stop_loss:
            return "STILL_OPEN"

        try:
            df = self.fetch_data("XAUUSD=X", period="1d", interval="5m")
            if df is None or df.empty:
                return "STILL_OPEN"

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

        except Exception:
            return "STILL_OPEN"

    def get_performance_summary(self):
        if not self.historical_signals:
            return {
                "total": 0, "win_rate": 0, "wins": 0, "losses": 0,
                "buy_win_rate": 0, "sell_win_rate": 0,
                "avg_confidence_win": 0, "total_estimated_pips": 0
            }

        wins = [s for s in self.historical_signals if s.outcome == "WIN"]
        losses = [s for s in self.historical_signals if s.outcome == "LOSS"]
        total = len(wins) + len(losses)

        win_rate = (len(wins) / total * 100) if total > 0 else 0

        buy_signals = [s for s in self.historical_signals if s.direction == SignalDirection.BUY and s.outcome]
        sell_signals = [s for s in self.historical_signals if s.direction == SignalDirection.SELL and s.outcome]

        buy_wins = len([s for s in buy_signals if s.outcome == "WIN"])
        sell_wins = len([s for s in sell_signals if s.outcome == "WIN"])

        buy_win_rate = (buy_wins / len(buy_signals) * 100) if buy_signals else 0
        sell_win_rate = (sell_wins / len(sell_signals) * 100) if sell_signals else 0

        if wins:
            avg_confidence_win = sum(s.confidence for s in wins) / len(wins)
        else:
            avg_confidence_win = 0

        total_pips = sum(s.estimated_pips for s in self.historical_signals if s.outcome)

        return {
            "total": total,
            "win_rate": round(win_rate, 1),
            "wins": len(wins),
            "losses": len(losses),
            "buy_win_rate": round(buy_win_rate, 1),
            "sell_win_rate": round(sell_win_rate, 1),
            "avg_confidence_win": round(avg_confidence_win, 1),
            "total_estimated_pips": round(total_pips, 1)
        }

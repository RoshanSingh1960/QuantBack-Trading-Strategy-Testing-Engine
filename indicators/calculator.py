import pandas as pd 
import ta 
 
class IndicatorCalculator: 
    def __init__(self): 
        pass 
 
    def add_sma(self, df: pd.DataFrame, window: int = 20, column: str = 'Close', name: str = None) -> pd.DataFrame: 
        name = name if name else f'SMA_{window}' 
        df[name] = ta.trend.sma_indicator(df[column], window=window, fillna=False) 
        return df 
 
    def add_ema(self, df: pd.DataFrame, window: int = 20, column: str = 'Close', name: str = None) -> pd.DataFrame: 
        name = name if name else f'EMA_{window}' 
        df[name] = ta.trend.ema_indicator(df[column], window=window, fillna=False) 
        return df 
 
    def add_rsi(self, df: pd.DataFrame, window: int = 14, column: str = 'Close', name: str = None) -> pd.DataFrame: 
        name = name if name else f'RSI_{window}' 
        df[name] = ta.momentum.rsi(df[column], window=window, fillna=False) 
        return df 
 
    def add_macd(self, df: pd.DataFrame, window_fast: int = 12, window_slow: int = 26, window_sign: int = 9, column: str = 'Close') -> pd.DataFrame: 
        macd = ta.trend.macd(df[column], window_fast=window_fast, window_slow=window_slow, fillna=False) 
        macd_signal = ta.trend.macd_signal(df[column], window_fast=window_fast, window_slow=window_slow, window_sign=window_sign, fillna=False) 
        macd_diff = ta.trend.macd_diff(df[column], window_fast=window_fast, window_slow=window_slow, window_sign=window_sign, fillna=False) 
 
        df['MACD'] = macd 
        df['MACD_Signal'] = macd_signal 
        df['MACD_Hist'] = macd_diff 
        return df 
 
    def add_all_common_indicators(self, df: pd.DataFrame, column: str = 'Close') -> pd.DataFrame: 
        """ONLY add SMA20 and SMA50 - nothing else to avoid excessive NaNs""" 
        df = self.add_sma(df, window=20, column=column, name='SMA_20')  
        df = self.add_sma(df, window=50, column=column, name='SMA_50')  
        return df  